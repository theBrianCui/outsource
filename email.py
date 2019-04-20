from utils import read_file_to_string, get_env, write_string_to_file

SEND_EMAIL_SCRIPT = "scripts/email.sh"
SENDGRID_API_KEY_ENV = "SENDGRID_API_KEY"

def create_email_script(recipient, subject="Outsource Job Completed", body="An Outsource job has been completed."):
    if not get_env("SENDGRID_API_KEY"):
        raise RuntimeError("SendGrid API key not present in ENV")

    email_script = read_file_to_string(SEND_EMAIL_SCRIPT)
    email_script = email_script.replace("SENDGRID_API_KEY", get_env("SENDGRID_API_KEY"))
    email_script = email_script.replace("RECIPIENT", recipient)
    email_script = email_script.replace("SUBJECT", subject)
    email_script = email_script.replace("BODY", body)

    temp_script_name = SEND_EMAIL_SCRIPT + ".tmp"
    write_string_to_file(email_script, temp_script_name, overwrite=True)
    return temp_script_name
