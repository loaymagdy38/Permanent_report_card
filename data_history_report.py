from common import load_contracts

w3, report, coin = load_contracts()
count = report.functions.studentCount().call()
all_grades = []
print("Student ID   Name                 Subject              Grade")
print("-" * 65)
for sid in range(1, count + 20):
    try:
        name, subject, grade = report.functions.getGrade(sid).call()
        all_grades.append(grade)
        print(f"{sid:<12} {name:<20} {subject:<20} {grade}")
    except Exception:
        pass
print("-" * 65)
if all_grades:
    print("Class average grade:", round(sum(all_grades) / len(all_grades), 2))
else:
    print("No grades found.")
