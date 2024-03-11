from onpoint_app.config.mysqlconnection import connectToMySQL
import re	# the regex module
from flask import flash  
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
class Provider:
    db_name = 'onpointsdb'
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.about = data['about']
        self.is_verified = data['is_verified']
        self.verification_code = data['verification_code']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_provider_by_email(cls, data):
        query = 'SELECT * FROM providers WHERE email= %(email)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
  

    @classmethod
    def get_provider_by_id(cls, data):
        query = 'SELECT * FROM providers WHERE id= %(provider_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
        
    @classmethod
    def updateVerificationCode(cls, data):
        query = "UPDATE providers SET verification_code = %(verification_code)s WHERE providers.id = %(provider_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def activateAccount(cls, data):
        query = "UPDATE providers set is_verified = 1 WHERE providers.id = %(provider_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data) 
    
    @classmethod
    def create_provider(cls, data):
        query = "INSERT INTO providers (first_name, last_name,  email, password, about, verification_code) VALUES ( %(first_name)s, %(last_name)s,%(email)s,%(password)s,%(about)s, %(verification_code)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_provider(cls, data):
        query = "UPDATE providers SET first_name = %(first_name)s, last_name = %(last_name)s, profession=%(profession)s, email= %(email)s, about=,%(about)s WHERE id = %(hr_id)s ;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_provider(cls, data):
        query = "DELETE FROM providers WHERE id = %(provider_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @staticmethod
    def validate_provider(provider):
        is_valid = True
        if not EMAIL_REGEX.match(provider['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(provider['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(provider['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        if len(provider['password'])< 8:
            flash('Password must be more or equal to 8 characters', 'password')
            is_valid = False
        if 'confirmpassword' in provider and provider['confirmpassword'] != provider['password']:
            flash('The passwords do not match',  'passwordConfirm')
            is_valid = False
        if len(provider['about'])< 8:
            flash('About must be more or equal to 8 characters', 'about')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_provider_update(provider):
        is_valid = True
        if not EMAIL_REGEX.match(provider['email']): 
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(provider['first_name'])< 2:
            flash('First name must be more than 2 characters', 'first_name')
            is_valid = False
        if len(provider['last_name'])< 2:
            flash('Last name must be more than 2 characters', 'last_name')
            is_valid = False
        if len(provider['about'])< 8:
            flash('About must be more or equal to 8 characters', 'about')
            is_valid = False
        return is_valid