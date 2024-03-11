from onpoint_app.config.mysqlconnection import connectToMySQL
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash

class Costumer:
    db_name="onpointsdb"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.is_verified = data['is_verified']
        self.verification_code = data['verification_code']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def get_costumer_by_email(cls, data):
        query = 'SELECT * FROM costumers WHERE email= %(email)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    @classmethod
    def get_costumer_by_id(cls, data):
        query = 'SELECT * FROM costumers WHERE id= %(costumer_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False

    @classmethod
    def create_costumer(cls, data):
        query = "INSERT INTO costumers (first_name, last_name, email,  password, verification_code) VALUES ( %(first_name)s, %(last_name)s,%(email)s,%(password)s, %(verification_code)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_costumer(cls, data):
        query = "UPDATE costumers SET first_name = %(first_name)s, last_name = %(last_name)s, email= %(email)s WHERE id = %(employee_id)s ;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def updateVerificationCode(cls, data):
        query = "UPDATE costumers SET verification_code = %(verification_code)s WHERE costumers.id = %(costumer_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def activateAccount(cls, data):
        query = "UPDATE costumers set is_verified = 1 WHERE costumers.id = %(costumer_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def delete_costumer(cls, data):
        query = "DELETE FROM costumers WHERE id = %(costumer_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @staticmethod
    def validate_costumer(costumer):
        is_valid = True
        if not EMAIL_REGEX.match(costumer['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(costumer['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(costumer['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        if len(costumer['password'])< 8:
            flash('Password must be more or equal to 8 characters', 'password')
            is_valid = False
        if 'confirmpassword' in costumer and costumer['confirmpassword'] != costumer['password']:
            flash('The passwords do not match',  'passwordConfirm')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_costumer_update(costumer):
        is_valid = True
        if not EMAIL_REGEX.match(costumer['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(costumer['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(costumer['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        return is_valid