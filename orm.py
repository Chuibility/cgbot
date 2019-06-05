from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

import config
import nonebot

engine = create_engine(config.DB_ENGINE['sqlite'])

Base = declarative_base()
 
class User(Base):
    __tablename__ = "Users"
 
    UserId = Column(Integer, primary_key=True)
    Name = Column(String)  

class Group(Base):
    __tablename__ = "Groups"
 
    GroupId = Column(Integer, primary_key=True)
    Name = Column(String)  

class UserInGroup(Base):
    __tablename__ = "UserInGroup"

    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"
    ROLE_SERVER = "server"

    Id = Column(Integer, primary_key=True)

    GroupId = Column(Integer, ForeignKey("Groups.GroupId"), nullable=False)
    UserId = Column(Integer, ForeignKey("Users.UserId"), nullable=False)
    Role = Column(String, nullable=False)
    Name = Column(String, nullable=False)

Session = sessionmaker(bind=engine)
_ses = Session()


# Updating Tables
Base.metadata.create_all(engine)

def getSession() -> Session:
    return _ses

def getUserByidOrCreate(ses: Session, Id : Integer):
    created = False
    usr = ses.query(User).filter(User.UserId == Id).one_or_none()
    if not usr:
        nonebot.logger.debug(f"Creating new user {Id}")
        usr = User(UserId = Id, Name = "Unknown")
        ses.add(usr)
        created = True
    return usr, created 

def getGroupByIdOrCreate(ses: Session, Id : Integer):
    created = False
    group = ses.query(Group).filter(Group.GroupId == Id).one_or_none()
    if not group:
        nonebot.logger.debug(f"Creating new Group {Id}")
        group = Group(GroupId = Id, Name = "Unknown")
        ses.add(group)
        created = True
    return group, created

def getUserInGroupOrCreate(ses : Session, user : User, group : Group):
    created = False
    affiliation = ses.query(UserInGroup).filter( 
        UserInGroup.UserId == user.UserId, 
        UserInGroup.GroupId == group.GroupId
    ).one_or_none()
    if not affiliation:
        nonebot.logger.debug(f"Creating new affilication {user.UserId} in {group.GroupId}")
        affiliation = UserInGroup(UserId=user.UserId, GroupId=group.GroupId, \
                                 Name="UnknownG", Role=UserInGroup.ROLE_MEMBER)
        ses.add(affiliation)
        created = True
    return affiliation, created

def is_admin(role):
    if role == ROLE_ADMIN:
        return True
    elif role == ROLE_SERVER:
        return True
    elif role == ROLE_MEMBER:
        return False
    else:
        raise Exception

if __name__ == "__main__" :
    # Initializes and creates the tables
    print("Dropping all tables.\n")
    Base.metadata.drop_all(engine)
    print("Initializing all tables.\n")
    Base.metadata.create_all(engine)

