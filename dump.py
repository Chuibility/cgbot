import orm

s = orm.getSession()

users = s.query(orm.User).all()

groups = s.query(orm.Group).all()

users_in_group = s.query(orm.UserInGroup).all()

for row in groups:
    print(f"Group (id = {row.GroupId})")

for row in users:
    print(f"User (id = {row.UserId}, Name = {row.Name})")

for row in users_in_group:
    print(f"Affil (id = {row.Id}, GID = {row.GroupId}, UID = {row.UserId}, Name = {row.Name})")