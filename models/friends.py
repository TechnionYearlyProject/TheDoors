from common.database import Database

"""
this class represent the friends table in the DB
the forrmat is like that:
 {'user_email_1': user1@email.com, 'user_email_2': user2@email.com }
 that means that user1 and user2 are friends
"""


def friends_key(user_email1, user_email2):
    if user_email1 < user_email2:
        return user_email1 + user_email2
    else:
        return user_email2 + user_email1


def json(user_email1, user_email2):
    _id = friends_key(user_email1, user_email2)
    return {
        '_id': _id,
        'user_email_1': user_email1,
        'user_email_2': user_email2
    }


class Friends(object):

    @staticmethod
    def save_to_mongodb(user_one, user_two):
        Database.insert(collection='friends', data=json(user_one, user_two))

    @staticmethod
    def add_friend(user_email, new_friend):
        """
        creates friends relationship between user_email and new friend iff:
        both of them are exist in the db
        both of them belongs to the same company
        they are'nt friends allready
        :param user_email:
        :param new_friend:
        :param company:
        :return:
        """

        if not Friends.is_friends(user_email, new_friend):
            #_id = friends_key(user_email, new_friend)
            Database.insert('friends', json(user_email, new_friend))
            #Friends.save_to_mongodb(user_email, new_friend)
            return True, "success"
        return False, "already friends"

    @staticmethod
    def remove_friend(user_email, to_remove):
        if Friends.is_friends(user_email, to_remove):
            _id = friends_key(user_email, to_remove)
            Database.remove('friends', {'_id': _id})
            return True, "success"
        else:
            return False, "aren't friends already"

    @staticmethod
    def get_friends(user_email):
        """
        :param user_email:
        :return: List of user_email's friends
        """
        friends_dict = Database.find('friends', {'$or': [{'user_email_1': user_email}, {'user_email_2': user_email}]})
        friends = []
        for friend in friends_dict:
            user1 = friend['user_email_1']
            user2 = friend['user_email_2']
            friend = user1 if user1 != user_email else user2
            friends.append(friend)
        return friends

    @staticmethod
    def is_friends(user_email, new_friend):
        """
        :param user_email:
        :param new_friend:
        :return: True if user_email and new_friend are friends, false else
        """
        _id = friends_key(user_email, new_friend)
        query = {'_id': _id}
        status = Database.find_one('friends', query)
        if status is not None:
            return True
        else:
            return False

    @staticmethod
    def remove_user(user_email):
        query = {'$or': [{'user_email_1': user_email}, {'user_email_2': user_email}]}
        Database.remove('friends', query)
