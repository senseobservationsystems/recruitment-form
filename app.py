from flask import Flask, redirect, render_template, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.jqueryuibootstrap import JqueryUiBootstrap as Bootstrap

from sqlite3 import IntegrityError
from slackclient import SlackClient
from hackerearth.api_handlers import HackerEarthAPI
from hackerearth.parameters import CompileAPIParameters, SupportedLanguages
from trello import TrelloApi

import pytz
import mandrill

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
Bootstrap(app)

POSITION = {
    "Android Developer": "template.java",
    "iOS Developer": "template.m"
}


def gen_text(applicant):
    return """\n
NAME : {}
EMAIL : {}
TEST DATE : {}
POSITION : {}
COVER LETTER : {}
LINKED_IN : {}
GITHUB : {}
ENGLISH PROFICIENCY : {}
TEST_URL : {}""".format(applicant.name,
                        applicant.email,
                        applicant.test_date.strftime('%d-%m-%Y %H:%M:%S'),
                        applicant.position,
                        applicant.cover_letter,
                        applicant.linkedin,
                        applicant.github,
                        applicant.english_proficiency,
                        applicant.test_url)


def send_message_slack(applicant):
    client = SlackClient(current_app.config['SLACK_TOKEN'])
    text = gen_text(applicant)

    client.api_call("chat.postMessage", channel=current_app.config['SLACK_CHANNEL'], text=text)


def create_test(applicant):
    template_name = POSITION[applicant.position]
    source = open(template_name)
    lang = SupportedLanguages.PYTHON
    params = CompileAPIParameters(
        client_secret=current_app.config['HACKEREARTH_SECRET_KEY'], source=source, lang=lang)
    api = HackerEarthAPI(params)
    r = api.compile()
    print r.__dict__
    applicant.test_url = r.__dict__['web_link']
    source.close()


def unschedule_email(applicant):
    mandrill_client = mandrill.Mandrill(current_app.config['MANDRILL_API_KEY'])
    result = mandrill_client.messages.list_scheduled(to=applicant.email)
    for email in result:
        mandrill_client.messages.cancel_scheduled(id=email["_id"])


def schedule_email(applicant):
    print applicant.test_date
    local = pytz.timezone('Asia/Jakarta')
    schedule_time = applicant.test_date.replace(tzinfo=local)
    print schedule_time
    schedule_time = schedule_time.astimezone(pytz.utc)
    print schedule_time

    mandrill_client = mandrill.Mandrill(current_app.config['MANDRILL_API_KEY'])
    message = {
        "global_merge_vars": [{'content': applicant.test_url, 'name': 'URL'},
                              {'content': applicant.name, 'name': 'NAME'}],
        "to": [{'email': applicant.email, 'type': 'to'}]
    }
    r = mandrill_client.messages.send_template(template_name=current_app.config['MANDRILL_TEMPLATE_NAME'],
                                               template_content=[],
                                               message=message,
                                               send_at=schedule_time.strftime('%Y-%m-%d %H:%M:%S'))

    print r


def update_trello(applicant):
    client = TrelloApi(current_app.config['TRELLO_API_KEY'])
    client.set_token(current_app.config['TRELLO_API_TOKEN'])

    desc = gen_text(applicant)

    client.lists.new_card(name=applicant.name, list_id=current_app.config['TRELLO_LIST_ID'], desc=desc)


@app.route('/application', methods=['GET', 'POST'])
def application():
    from forms import ApplicantForm
    from models import ApplicantModel
    form = ApplicantForm()
    if form.validate_on_submit():
        applicant = db.session.query(ApplicantModel).filter_by(email=form.email.data).first()
        if not applicant:
            applicant = ApplicantModel()
            db.session.add(applicant)
        else:
            unschedule_email(applicant)

        form.populate_obj(applicant)
        create_test(applicant)
        schedule_email(applicant)
        update_trello(applicant)
        send_message_slack(applicant)
        db.session.commit()

        return render_template('success.html')

    return render_template('application.html', form=form)


if __name__ == "__main__":
    app.run()
