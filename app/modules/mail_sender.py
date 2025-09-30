from app.models import insert_mailing_record_sqlalchemy


def send_email(target, subject, content,
                                    html_template=None,
                                    attachment_name=None,
                                    attachment_content=None,
                                    session=None):

    success = insert_mailing_record_sqlalchemy(
        session=session,
        target=target,
        subject=subject,
        content=content,
        html_template=html_template,
        attachment_name=attachment_name,
        attachment_content=attachment_content
    )

    if success:
        return True
    else:
        return False


