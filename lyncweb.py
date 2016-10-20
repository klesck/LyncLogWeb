from flask import Flask, render_template
from rtf import Rtf2Txt
from sqlalchemy import create_engine, Column, Integer, DATETIME, Text, NVARCHAR, BIGINT, INT, and_, or_, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import re

app = Flask(__name__)
app.config.from_pyfile('config.py')


engine = create_engine('mssql+pymssql://user:password@mssql:1433/LcsLog')
Base = declarative_base()
session = sessionmaker()
session.configure(bind=engine)
s = scoped_session(session)


class Users(Base):
    __tablename__ = "Users"
    NextUpdateTS = Column(DATETIME)
    UserId = Column(Integer, primary_key=True)
    UserUri = Column(NVARCHAR)
    TenantId = Column(Integer)
    UriTypeId = Column(Integer)


class Messages(Base):
    __tablename__ = 'Messages'
    MessageIdTime = Column(DATETIME, primary_key=True)
    MessageIdSeq = Column(Integer, primary_key=True)
    SessionIdTime = Column(DATETIME, primary_key=True)
    SessionIdSeq = Column(Integer, primary_key=True)
    FromId = Column(Integer)
    ToId = Column(Integer)
    ContentTypeId = Column(Integer)
    ServerId = Column(Integer)
    Body = Column(Text)
    Toast = Column(BIGINT)
    ContextNote = Column(BIGINT)
    Subject = Column(BIGINT)
    Reserved1 = Column(INT)
    Reserved2 = Column(INT)


def rtf_to_txt(string):
    try:
        converted = Rtf2Txt.getTxt(string)
    except UnicodeDecodeError:
        converted = 'err'
    return converted


def remove_tags(text):
    tag_remove = re.compile(r'<[^>]+>')
    only_text = tag_remove.sub('', text)
    return [line for line in only_text.split('\n') if line.strip() != '']


@app.route('/')
def index():
    users = s.query(Users.UserId, Users.UserUri).all()
    return render_template('index.html', users=users)


@app.route('/<int:uid>')
def user_chats(uid):
    users = s.query(Users.UserId, Users.UserUri).all()
    messages = s.query(Messages.ToId).filter(Messages.FromId == uid).order_by(desc(Messages.MessageIdTime))
    messages = reduce(lambda l, x: l.append(x) or l if x not in l else l, messages, [])
    dates = []
    for i in messages:
        dates.append(s.query(Messages.MessageIdTime).filter(Messages.FromId == uid, Messages.ToId == i[0]).order_by(
            desc(Messages.MessageIdTime)).first())
    return render_template('user_chats.html', users=users, messages=messages, uid=uid, dates=dates)


@app.route('/<int:uid>/<int:uid2>')
def users_conversation(uid, uid2):
    users = s.query(Users.UserUri, Users.UserId).filter(or_(Users.UserId == uid, Users.UserId == uid2)).all()
    messages = s.query(Messages.Body, Messages.ContentTypeId, Messages.FromId, Messages.MessageIdTime).filter\
        (or_(and_(Messages.FromId == uid, Messages.ToId == uid2),
             (and_(Messages.FromId == uid2, Messages.ToId == uid)))).all()
    message = []
    for i in messages:
        if i[1] == 2:
            work_list = []
            work_list.append(i[3].strftime('%d-%b-%y %H:%M'))
            work_list.append(i[2])
            work_list.append(rtf_to_txt(i[0]))
            message.append(work_list)
        if i[1] == 1:
            work_list = []
            work_list.append(i[3].strftime('%d-%b-%y %H:%M'))
            work_list.append(i[2])
            text = remove_tags(i[0])
            work_list.append(' '.join(text))
            message.append(work_list)

    return render_template('users_conversation.html', messages=message, users=users)


if __name__ == '__main__':
    app.run()
