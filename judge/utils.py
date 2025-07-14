import re
import subprocess
import tempfile
import os
import time
from judge.models import Submission, TestCase, SubmissionResult

def is_valid_username(username):
    return bool(re.fullmatch(r'[a-zA-Z0-9]{5,15}', username))

def is_strong_password(password):
    if len(password) < 8 or len(password) > 32:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[\W_]', password):
        return False
    return True

def docker_run(image, command, mount_dir, input_data, timeout, memory_limit="256m"):
    return subprocess.run(
        ["docker", "run", "-i", "--rm",
         "-v", f"{mount_dir}:/app",
         "--network=none",
         f"--memory={memory_limit}",
         "--cpus=0.5",
         image,
         "/usr/bin/time", "-v"] + command,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        text=True
    )

def parse_time_verbose_output(stderr_output: str) -> dict:
    result = {}
    patterns = {
        'user_time': r'User time \(seconds\): ([\d.]+)',
        'system_time': r'System time \(seconds\): ([\d.]+)',
        'elapsed_time': r'Elapsed \(wall clock\) time.*: ([\d.:]+)',
        'cpu_percent': r'Percent of CPU this job got: ([\d.]+)%',
        'max_memory_kb': r'Maximum resident set size \(kbytes\): (\d+)',
        'exit_status': r'Exit status: (\d+)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, stderr_output)
        if match:
            value = match.group(1)
            if key in ['user_time', 'system_time', 'cpu_percent']:
                result[key] = float(value)
            elif key == 'max_memory_kb':
                result[key] = int(value)
            elif key == 'exit_status':
                result[key] = int(value)
            else:
                result[key] = value
    return result

def judge_submission(submission_id):
    try:
        submission = Submission.objects.get(id=submission_id)
        problem = submission.problem
        testcases = TestCase.objects.filter(problem=problem)

        language_settings = {
            "py": {
                "filename": "main.py",
                "compile_cmd": None,
                "run_cmd": ["python3", "/app/main.py"],
                "docker_image": "oj-python"
            },
            "c": {
                "filename": "main.c",
                "compile_cmd": ["gcc", "/app/main.c", "-o", "/app/main", "-lm"],
                "run_cmd": ["/app/main"],
                "docker_image": "oj-gcc"
            },
            "cpp": {
                "filename": "main.cpp",
                "compile_cmd": ["g++", "/app/main.cpp", "-o", "/app/main"],
                "run_cmd": ["/app/main"],
                "docker_image": "oj-gcc"
            },
            "java": {
                "filename": "Main.java",
                "compile_cmd": ["javac", "/app/Main.java"],
                "run_cmd": ["java", "-cp", "/app", "Main"],
                "docker_image": "oj-java"
            }
        }

        lang = submission.language.code
        if lang not in language_settings:
            submission.status = "COMPILE_ERROR"
            submission.save()
            return

        config = language_settings[lang]

        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = os.path.join(tmpdir, config["filename"])
            with open(code_path, "w") as f:
                f.write(submission.code)

            # Compile if needed
            if config["compile_cmd"]:
                try:
                    compile_result = docker_run(
                        image=config["docker_image"],
                        command=config["compile_cmd"],
                        mount_dir=tmpdir,
                        input_data="",
                        timeout=5
                    )
                    if compile_result.returncode != 0:
                        submission.status = "COMPILE_ERROR"
                        submission.save()
                        return
                except Exception:
                    submission.status = "COMPILE_ERROR"
                    submission.save()
                    return

            all_passed = True

            for tc in testcases:
                try:
                    start = time.time()
                    result = docker_run(
                        image=config["docker_image"],
                        command=config["run_cmd"],
                        mount_dir=tmpdir,
                        input_data=tc.input_data,
                        timeout=problem.time_limit,
                        memory_limit=f"{problem.memory_limit}m"
                    )
                    elapsed = time.time() - start
                    stats = parse_time_verbose_output(result.stderr)

                    memory_used_mb = stats.get("max_memory_kb", 0) / 1024.0
                    output = result.stdout.strip()
                    expected = tc.expected_output.strip()

                    status = "ACCEPTED" if output == expected else "WRONG_ANSWER"
                    if memory_used_mb > problem.memory_limit:
                        status = "MLE"

                    if status != "ACCEPTED":
                        all_passed = False

                    SubmissionResult.objects.create(
                        submission=submission,
                        test_case=tc,
                        actual_output=output,
                        expected_output=expected,
                        execution_time=elapsed,
                        memory_used=memory_used_mb,
                        status=status,
                        message=result.stderr
                    )

                except subprocess.TimeoutExpired:
                    all_passed = False
                    SubmissionResult.objects.create(
                        submission=submission,
                        test_case=tc,
                        actual_output="",
                        expected_output=tc.expected_output.strip(),
                        execution_time=None,
                        memory_used=None,
                        status="TLE",
                        message=f"Quá thời gian (> {problem.time_limit}s)"
                    )
                except Exception as e:
                    all_passed = False
                    SubmissionResult.objects.create(
                        submission=submission,
                        test_case=tc,
                        actual_output="",
                        expected_output=tc.expected_output.strip(),
                        execution_time=None,
                        memory_used=None,
                        status="RUNTIME_ERROR",
                        message=str(e)
                    )

            submission.status = "SUBMITTED" if all_passed else "SUBMITTED"
            submission.save()

    except Exception as e:
        try:
            submission = Submission.objects.get(id=submission_id)
            submission.status = "SYSTEM_ERROR"
            submission.save()
        except:
            pass
