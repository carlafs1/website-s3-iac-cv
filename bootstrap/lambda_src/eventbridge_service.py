####----------------------------------------------------------------------------------------####
####----              Reagenda o horário para acionar destroy do site efêmero           ----####
####----------------------------------------------------------------------------------------####

from aws_clients import events
from config import EVENTBRIDGE_RULE


def reschedule_eventbridge(next_run):
    print("Iniciando reagendamento do EventBridge.")

    if not EVENTBRIDGE_RULE:
        print("EVENTBRIDGE_RULE não definida. Reagendamento ignorado.")
        return

    expression = (
        f"cron({next_run.minute} "
        f"{next_run.hour} "
        f"{next_run.day} "
        f"{next_run.month} "
        f"? "
        f"{next_run.year})"
    )

    print(f"Rule: {EVENTBRIDGE_RULE}")
    print(f"Próxima execução: {next_run.isoformat()}")
    print(f"Nova expressão cron: {expression}")

    events.put_rule(
        Name=EVENTBRIDGE_RULE,
        ScheduleExpression=expression,
        State="ENABLED"
    )

    print("EventBridge reagendado com sucesso.")