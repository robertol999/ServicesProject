from onpoint_app.config.mysqlconnection import connectToMySQL
from flask import flash  

class Job:
    db_name = 'onpointsdb'
    def __init__(self , data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.address = data['address']
        self.education_experience = data['education_experience']
        self.city = data['city']
        self.employment_status = data['employment_status']
        self.experience = data['experience']
        self.deadline = data['deadline']
        self.job_post_image = data['job_post_image']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.star_rating= data['star_rating']
        
    @classmethod
    def update(cls, data):
        query = "UPDATE jobs set description = %(description)s, address=%(address)s, education_experience = %(education_experience)s,city = %(city)s,experience = %(experience)s,employment_status = %(employment_status)s WHERE jobs.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)   
        
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM jobs WHERE id = %(job_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def count_jobs(cls):
        query = 'SELECT COUNT(*) FROM jobs;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    
    @classmethod
    def get_job_by_id(cls, data):
        query = 'SELECT * FROM jobs WHERE id= %(job_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    @classmethod
    def get_all_jobs(cls):
        query = 'SELECT * FROM jobs;'
        results = connectToMySQL(cls.db_name).query_db(query)
        jobs = []
        if results:
            for job in results:
                job = Job(job)
                jobs.append(job)
            return jobs
        return jobs
    @classmethod
    def update_star_rating(cls, job_id, rating):
        query = "UPDATE jobs SET star_rating = %(rating)s WHERE id = %(job_id)s;"
        data = {
            'job_id': job_id,
            'rating': rating
        }
        connectToMySQL(cls.db_name).query_db(query, data) 
    @classmethod
    def delete_all_job_ratings(cls, data):
        query ="DELETE FROM ratings where ratings.job_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    @classmethod
    def search(cls, search_query):

        query = f"""
            SELECT * FROM jobs where jobs.title LIKE '{search_query}%'
        """

        try:
            results = connectToMySQL(cls.db_name).query_db(query)

            jobs = []
            if results:
                for job in results:
                    jobs.append(job)
            return jobs
        except Exception as e:
            print("An error occurred:", str(e))
            return []
    @classmethod
    def createPayment(cls,data):
        query = "INSERT INTO payments (ammount, status, job_id) VALUES (%(ammount)s, %(status)s, %(job_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_allUserPayments(cls, data):
        query = "SELECT * FROM payments where costumer_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        payments = []
        if results:
            for pay in results:
                payments.append(pay)
        return payments    
    
    @classmethod
    def get_provider_jobs_by_id(cls, data):
        query = 'SELECT * FROM jobs WHERE provider_id= %(provider_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        return results 
    
    @classmethod
    def get_job_creator(cls, data):
        query="SELECT jobs.id AS job_id, jobs.provider_id, providers.id AS provider_id, provider.first_name as first_name, providers.last_name as last_name, profession,email FROM jobs LEFT JOIN providers ON jobs.provider_id = providers.id WHERE jobs.id= %(job_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def create_job(cls, data):
        query = "INSERT INTO jobs (title, description, address, education_experience, city, employment_status, experience, deadline, job_post_image,  provider_id) VALUES ( %(title)s, %(description)s, %(address)s, %(education_experience)s, %(city)s, %(employment_status)s, %(experience)s, %(deadline)s, %(job_post_image)s, %(provider_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @staticmethod
    def validateImage(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'job_post_image')
            is_valid = False 
        return is_valid
    
    @staticmethod
    def validateImageLogo(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'company_logo')
            is_valid = False 
        return is_valid
    
    @staticmethod
    def validate_job(provider):
        is_valid = True
        if len(provider['title'])< 3:
            flash('Title must be more than 2 characters', 'title')
            is_valid = False
        if len(provider['description'])< 3:
            flash('Description must be more than 2 characters', 'description')
            is_valid = False
        if  len(provider['address'])< 3:
            flash('Salary must be more or equal to 8 characters', 'address')
            is_valid = False
        if len(provider['education_experience'])< 4:
            flash('Education and Experience must be more or equal to 4 characters', 'education_experience')
            is_valid = False
        if len(provider['city'])< 4:
            flash('Benefits must be more or equal to 4 characters', 'city')
            is_valid = False
        if not (provider['employement_status']):
            flash('Choose Employement status', 'employement_status')
            is_valid = False
        if len(provider['experience'])> 3:
            flash(' Enter a valid experience', 'experience')
            is_valid = False
        return is_valid
    