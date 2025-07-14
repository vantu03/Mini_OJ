import re
import subprocess
import tempfile
import os
import time
from judge.models import Submission, TestCase


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
         image] + command,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        text=True
    )



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
                "compile_cmd": ["gcc", "/app/main.c", "-o", "/app/main"],
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
            submission.verdict = "COMPILE_ERROR"
            submission.error_message = "Ngôn ngữ không hỗ trợ"
            submission.save()
            return

        config = language_settings[lang]

        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = os.path.join(tmpdir, config["filename"])
            with open(code_path, "w") as f:
                f.write(submission.code)

            # Biên dịch nếu cần
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
                        submission.verdict = "COMPILE_ERROR"
                        submission.error_message = compile_result.stderr
                        submission.save()
                        return
                except subprocess.TimeoutExpired:
                    submission.verdict = "COMPILE_ERROR"
                    submission.error_message = "Quá thời gian khi biên dịch"
                    submission.save()
                    return
                except Exception as e:
                    submission.verdict = "COMPILE_ERROR"
                    submission.error_message = str(e)
                    submission.save()
                    return

            # Chạy từng test case
            for tc in testcases:
                try:
                    start = time.time()
                    result = docker_run(
                        image=config["docker_image"],
                        command=config["run_cmd"],
                        mount_dir=tmpdir,
                        input_data=tc.input_data,
                        timeout=problem.time_limit,
                        memory_limit=f"{problem.memory_limit}m"  # ⚠️ thêm dòng này
                    )
                    elapsed = time.time() - start

                    output = result.stdout.strip()
                    expected = tc.expected_output.strip()

                    if output != expected:
                        submission.verdict = "WRONG_ANSWER"
                        submission.error_message = f"Sai output ở test case\nExpected: {expected}\nGot: {output}"
                        submission.save()
                        return

                except subprocess.TimeoutExpired:
                    submission.verdict = "TLE"
                    submission.error_message = f"Quá thời gian (>{problem.time_limit}s)"
                    submission.save()
                    return
                except Exception as e:
                    submission.verdict = "RUNTIME_ERROR"
                    submission.error_message = str(e)
                    submission.save()
                    return

        submission.verdict = "ACCEPTED"
        submission.error_message = ""
        submission.save()

    except Exception as e:
        try:
            submission = Submission.objects.get(id=submission_id)
            submission.verdict = "SYSTEM_ERROR"
            submission.error_message = f"Lỗi hệ thống: {str(e)}"
            submission.save()
        except:
            pass
