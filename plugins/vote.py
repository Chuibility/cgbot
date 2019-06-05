from nonebot import on_command, CommandSession, logger
from nonebot import Message, MessageSegment
from nonebot.argparse import ArgumentParser
from nonebot.typing import Context_T
import nonebot, sys

from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey

import handlers
import orm

bot = nonebot.get_bot()

class VoteItem(orm.Base) :
    __tablename__ = "VoteItems"

    Id = Column(Integer, primary_key=True)

    GroupId = Column(Integer, ForeignKey("Groups.GroupId"), nullable=False)
    ProposerId = Column(Integer, ForeignKey("Users.UserId"), nullable=False)
    Name = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    Committed = Column(Boolean, nullable=False)

class Vote(orm.Base) :
    __tablename__ = "Votes"

    Id = Column(Integer, primary_key=True)
    Item = Column(Integer, ForeignKey("VoteItems.Id"), nullable=False)
    Voter = Column(Integer, ForeignKey("Users.UserId"), nullable=False)
    Ballot = Column(String, nullable=False)

# Set-up the DBs if necessary
orm.Base.metadata.create_all(orm.engine)

USAGE=r"""
Voting Command: /vote command item ...
/vote list [all] : Lists open (all) voting items
/vote new ITEM desc : Initiate a new vote "ITEM"
/vote yea ITEM : Vote Yes to ITEM
/vote nay ITEM : Vote No to ITEM
/vote commit ITEM : [OWNER] Concludes vote ITEM
/vote count ITEM : Prints users voting Yes to ITEM
/vote annouce ITEM : [OWNER] Announces result. 
""".strip()

class _VoteItemNotFound(Exception):
    pass

class _NotVoteOwner(Exception):
    pass

class _VoteClosed(Exception):
    pass

_BALLOT_YEA = "yea"
_BALLOT_NAY = "nay"
_BALLOT_ABSTAIN = "abstain"

@on_command('vote', shell_like=True)
@handlers.on_GroupCommand("vote")
async def vote(s : CommandSession, user, group, user_in_group, state):
    parser = ArgumentParser(session=s, usage=USAGE)
    parser.add_argument('command', choices=[
        'list', 'new', 'yea', 'nay', 'commit', 
        'count', 'announce'
        ])
    parser.add_argument('ITEM')
    parser.add_argument('extra', nargs='?')
    args = parser.parse_args(s.argv)
    
    name = args.ITEM.strip()
    db : orm.Session = orm.getSession()
    vote_item = db.query(VoteItem).filter(
        VoteItem.GroupId == group.GroupId,
        VoteItem.Name == name
    ).one_or_none()
    try:
        if args.command == 'list':
            msg = Message("List of available vote items:\n")
            items = None
            if args.extra == 'all': 
                # Extract all items
                items = db.query(VoteItem).filter(VoteItem.GroupId == group.GroupId).all()
            else:
                # Extract active items
                items = db.query(VoteItem).filter(
                    VoteItem.GroupId == group.GroupId, 
                    VoteItem.Committed == False
                    ).all()
            for item in items:
                msg.append(MessageSegment.text(f"'{item.Name}' - {item.Description}\n"))
            await s.send(msg)
            
        elif args.command == 'new':
            if not vote_item:
                if not args.extra:
                    desc = f"Vote on {name}"
                else:
                    desc = args.extra
                item = VoteItem(GroupId=group.GroupId, ProposerId=user.UserId, 
                                Name=name, Committed=False, Description=desc
                        )
                db.add(item)
                db.commit()
                await s.send(f"Vote item '{item.Description}' ({item.Name}) created.", at_sender=True)
            else:
                await s.send(f"Vote item '{vote_item.Name}' already exisist.", at_sender=True)
        elif args.command == 'yea':
            if not vote_item:
                raise _VoteItemNotFound()
            if vote_item.Committed:
                raise _VoteClosed()
            vote = db.query(Vote).filter(
                Vote.Item == vote_item.Id,
                Vote.Voter == user.UserId
            ).one_or_none()
            if not vote:
                vote = Vote(Item=vote_item.Id, Voter=user.UserId, Ballot=_BALLOT_YEA)
                db.add(vote)
            else:
                vote.Ballot = _BALLOT_YEA
            db.commit()
            await s.send(f"You voted YES to '{vote_item.Description}' ({vote_item.Name}).", at_sender=True)

        elif args.command == 'nay':
            if not vote_item:
                raise _VoteItemNotFound
            if vote_item.Committed:
                raise _VoteClosed
            vote = db.query(Vote).filter(
                Vote.Item == vote_item.Id,
                Vote.Voter == user.UserId
            ).one_or_none()
            if not vote:
                vote = Vote(Item=vote_item.Id, Voter=user.UserId, Ballot=_BALLOT_NAY)
                db.add(vote)
            else:
                vote.Ballot = _BALLOT_NAY
            db.commit()
            await s.send(f"You voted NO to '{vote_item.Description}' ({vote_item.Name}).", at_sender=True)

        elif args.command == 'commit':
            if not vote_item:
                raise _VoteItemNotFound()
            if vote_item.ProposerId != user.UserId:
                raise _NotVoteOwner()
            vote_item.Committed = True
            db.commit()
            await s.send(f"You concluded vote item '{vote_item.Description}' ({vote_item.Name}).", at_sender=True)

        elif args.command == 'count':
            if not vote_item:
                raise _VoteItemNotFound
            total_count = db.query(Vote).filter(Vote.Item==vote_item.Id).count()
            positives = db.query(Vote).filter(Vote.Item==vote_item.Id, Vote.Ballot==_BALLOT_YEA).count()
            await s.send(f"Vote item '{vote_item.Description}' ({vote_item.Name}) got {positives} YES among {total_count} votes.")
        
        elif args.command == 'announce':
            if not vote_item:
                raise _VoteItemNotFound
            total_count = db.query(Vote).filter(Vote.Item==vote_item.Id).count()
            # proposer = db.query(orm.User).filter(orm.User.UserId==vote_item.ProposerId).one()
            positives = db.query(Vote).filter(
                Vote.Item == vote_item.Id, 
                Vote.Ballot == _BALLOT_YEA
                ).all()
            # positives = db.query(Vote, orm.User) \
            #               .join(Vote.Voter == orm.User.UserId) \
            #               .filter(Item=vote_item.Id, Ballot=_BALLOT_YEA) \
            #               .all()
            msg = nonebot.Message(f"Vote item '{vote_item.Description}' ({vote_item.Name}) initiated by ") 
            msg.append(MessageSegment.at(vote_item.ProposerId))
            msg.append(MessageSegment.text(f" got {len(positives)} YES among {total_count} votes. "))
            msg.append(MessageSegment.text(f"The following users in favor of the item:"))
            segs = [nonebot.MessageSegment.at(vote.Voter) for vote in positives]
            for seg in segs:
                msg.append(seg)
            await s.send(msg)
        else:
            raise Exception

    except _VoteItemNotFound:
        await s.send(f"Vote item '{name}' does not exist.", at_sender=True)

    except _NotVoteOwner:
        await s.send(f"You does not own vote item '{name}'.", at_sender=True)

    except _VoteClosed:
        await s.send(f"Voting for '{name}' is already closed.", at_sender=True)