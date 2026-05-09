import time
from common import load_contracts

w3, report, coin = load_contracts()

topic_hash = w3.keccak(text="GradeChanged(uint256,string,string,uint256)").hex()
if not topic_hash.startswith("0x"):
    topic_hash = "0x" + topic_hash

last_block = w3.eth.block_number

print("Live grade alert running. Press Ctrl+C to stop.")
print("Watching for GradeChanged events only...")

while True:
    try:
        current_block = w3.eth.block_number

        if current_block > last_block:
            for block_number in range(last_block + 1, current_block + 1):
                logs = w3.eth.get_logs({
                    "fromBlock": block_number,
                    "toBlock": block_number,
                    "address": report.address,
                    "topics": [topic_hash],
                })

                for log in logs:
                    try:
                        event_data = report.events.GradeChanged().process_log(log)
                        student_id = event_data["args"]["studentId"]
                        student_name = event_data["args"]["studentName"]
                        subject = event_data["args"]["subject"]
                        grade = event_data["args"]["grade"]

                        print(
                            f"ALERT: A grade change just happened! "
                            f"ID={student_id}, Name={student_name}, "
                            f"Subject={subject}, Grade={grade}"
                        )
                    except Exception:
                        print("ALERT: A grade change just happened!")

            last_block = current_block

        time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopped live alert.")
        break

    except Exception:
        print("Alert check failed. Please make sure Ganache is running and setup.py was executed.")
        time.sleep(2)
