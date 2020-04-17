import sqlite3

from flask import Flask, g, request, jsonify
from functools import wraps

app = Flask(__name__)

api_username = "admin"
api_password = "password"


def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({'message': 'Authentication failed!'}), 401

    return decorated


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def connect_db():
    sql = sqlite3.connect('/mnt/c/Users/prana/PycharmProjects/memberapi/members.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    members_cur = db.execute('select id, name, email,level from members')
    members = members_cur.fetchall()
    return_values = []
    for member in members:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']
        return_values.append(member_dict)

    # username = request.authorization.username
    # password = request.authorization.password
    # return json objects to Front View
    # if username == api_username and password == api_password:
    #  return jsonify({'members': return_values, 'username': username, 'password': password})
    return jsonify({'members': return_values})
    # return jsonify({'message': 'Authentication Failed'}), 401
    # return 'This return all the members!'


@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('select id, name , email, level from members where id =?', [member_id])
    member = member_cur.fetchone()
    return jsonify(
        {'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})
    # return 'This returns one member by ID'


@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('insert into members (name, email, level) values(?,?,?)', [name, email, level])
    db.commit()
    mem_cur = db.execute('select id, name, email, level from members where name = ?', [name])
    new_member = mem_cur.fetchone()

    return jsonify({"member": {"id": new_member["id"], "name": new_member["name"], "email": new_member["email"],
                               "level": new_member["level"]}})
    # return ''' The name is {}, \n the email is {}, \n the level is {}'''.format(name, email, level)


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    update_member_content = request.get_json()
    uname = update_member_content['name']
    uemail = update_member_content['email']
    ulevel = update_member_content['level']

    db = get_db()
    db.execute('update members set name = ?, email = ?,level= ? where id =?',
               [uname, uemail, ulevel, member_id])
    db.commit()
    member_u_cur = db.execute('select id, name, email ,level from members where id =?', [member_id])
    new_member = member_u_cur.fetchone()
    return jsonify({'member': {
        'id': new_member['id'], 'name': new_member['name'], 'email': new_member['email'], 'level': new_member['level']
    }})
    # return 'This updates a member by ID'


@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute('delete from members where id =?',
               [member_id])
    db.commit()

    return jsonify({'member': 'The member has been deleted'})
    # return 'This removes a member by ID'


if __name__ == '__main__':
    app.run(debug=True)
