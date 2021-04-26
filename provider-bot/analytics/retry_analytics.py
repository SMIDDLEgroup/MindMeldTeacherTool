from collections import Counter

timestamp = "20210401121702"

with open(f'../loggs/{timestamp}.txt') as f:
    log = f.read()


with open(f'../loggs/states{timestamp}.txt') as f:
    states_log = f.read()


messages = states_log.split("==========================\n")
parsed_messages = []
for msg in messages:
    fields = msg.split(":::\n")
    parsed_messages.append(dict(zip(['timestamp', 'username', 'state', 'intent', 'entities', 'request', 'directives'], fields)))
parsed_messages = parsed_messages[:-1]

with open(f'./reports/{timestamp}report.txt', 'w') as report:
    users_count = Counter([m['username'] for m in parsed_messages])
    report.write(f"Count of users: {len(users_count)}\n")
    report.write(f"Average messages count: {len(parsed_messages) / len(users_count)}\n")

    report.write("\n")

    report.write("Intents\n")
    intent_count = Counter([m['intent'] for m in parsed_messages])
    for (intent, count) in intent_count.most_common(100):
        report.write(f"{intent}: {count / len(parsed_messages) * 100}%\n")

    report.write('\n')

    report.write("States\n")
    states_count = Counter([m['state'] for m in parsed_messages])
    for (state, count) in states_count.most_common(100):
        report.write(f"{state}: {count / len(parsed_messages) * 100}%\n")

    report.write('\n')

    operator_calls = 0
    for m in parsed_messages:
        if 'з оператором' in m['directives']:
            operator_calls += 1

    report.write(f'Operator calls: {operator_calls}\n')

    failed = 0
    for m in parsed_messages:
        if 'Не вдалося' in m['directives']:
            failed += 1

    report.write(f'Not recognized: {failed}\n')