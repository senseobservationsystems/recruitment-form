from app import db


class ApplicantModel(db.Model):
    id = db.Column('applicant_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    test_date = db.Column(db.DateTime)
    position = db.Column(db.String(100))
    cover_letter = db.Column(db.Text)
    linkedin = db.Column(db.String(100))
    github = db.Column(db.String(100))
    english_proficiency = db.Column(db.Integer)
    test_url = db.Column(db.String(100))
