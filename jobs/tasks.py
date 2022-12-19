from __future__ import absolute_import, unicode_literals
from asyncio import sleep
import random
import time
from .models import Job, Skill
from celery import shared_task
import cloudscraper
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from django.db.models import Q 

skills_list=['Python','SQL','AWS', 'Machine learning','Deep learning','Text mining',
        'NLP','SAS','Tableau','Sagemaker','Tensorflow','Spark', 'numpy', 'MongDB','PSQL',
        "Postgres", 'Pandas', 'RESTFUL','NLP','Statistics','Algorithms','Visualization',
        'GCP','Google Cloud','Naive Bayes','Random Forest','Bachelors degree','Masters degree'
        'Java','Pyspark','Postgres','MySQL','Github','Docker','Machine Learning','C+',
        'C++','Pytorch','Jupyter Notebook','R Studio','R-Studio','Forecasting','Hive',
        'PhD','GCP','Numpy','NoSQL','Neo4j','Neural Network','Clustering','Linear Algebra',
        'Google Colab','Data Mining','Regression','Time Series','ETL','Data Wrangling',
        'Web Scraping','Feature Extraction','Featuring Engineering','Scipy','ML','DL']
    

@shared_task()
def start_scraping():
    
    Job.objects.all().delete()

        
    indeed_scrapper = IndeedScrapper()
    jobmaster_scrapper = JobmasterScrapper()
    drushim_scrapper = DrushimScrapper()
    
    jobmaster_result = jobmaster_scrapper.start('python', 'אשדוד+ואשקלון')
    indeed_result = indeed_scrapper.start('python', 'ashdod')
    drushim_result = drushim_scrapper.start('python', '1')

    save_jobs_to_database(jobmaster_result)
    save_jobs_to_database(indeed_result)
    save_jobs_to_database(drushim_result)




def sleep_for_random_interval():
    delay = random.randint(1,5)
    time.sleep(delay)
          
def save_jobs_to_database(job):
              
    try: 
        is_job_url_unique = Job.objects.filter(url=job['url']).exists() == False
                    
        if is_job_url_unique : 
            
            
            Job.objects.create(
                title=job['title'],
                company = job['company'],
                location = job[ 'location'],
                date_posted = job['date'],
                description = job['description'],
                url = job['url'],    
            )
        
    except Exception as e:
        print(e)
        print('task falied an error occured')
                        
def save_jobs_to_database(jobs_list):
    
    skills = Skill.objects.all()

    for job in jobs_list:
                
        try:
            
            is_job_unique = Job.objects.filter(url=job['url']).exists() == False and len(job['skills']) > 0
                        
            if is_job_unique : 

                
                job_object = Job(title=job['title'],company=job['company'], location=job['location'], description=['description'], url=job['url'])
                job_object.save()
                
                
                job_skill_list = job['skills']
                job_skills_to_add = set()
                
                for skill in skills:
                    
                    current_skill = skill.description.lower()
                    
                    if(current_skill in job_skill_list):
                        job_skills_to_add.add(skill)

                job_object.skills.set(job_skills_to_add)
                job_object.save()
           
            

        except Exception as e:
            print(e)
            print('task falied an error occured')


        
class JobmasterScrapper:
    

    def __init__(self):
        self.url_template = "https://www.jobmaster.co.il/jobs/?q={}&l={}"

        
    def request_from_indeed(self, url):
        
        scraper = cloudscraper.create_scraper()  
        response = scraper.get(url=url)
        
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            return None
    
    
    def get_qualifactions(self, url):
        
        qualifactions_list = []
        soup = self.request_from_indeed(url)
        
        try:
            qualifactions = soup.find('div',{'class':'article__jobBody'})
            
            for qualifaction in qualifactions:
                try:
                    qualifactions_list.append(''.join(qualifaction.text.strip()))
                except AttributeError:
                    qualifactions_list.append('')   
        except AttributeError:
            qualifactions_list = []
            
        return qualifactions_list


    def extract_job_card_data(self, card):
        
            try:
                title = card.find('a', 'CardHeader').text.strip()  
            except AttributeError:
                title= ''
            try:
                company = card.find('div', 'paddingTop10px').span.text.strip()
            except AttributeError:
                company = ''
            try:
                location = card.find('li', 'jobLocation').text.strip()
            except AttributeError:
                location = ''
          
            try:
                posted_at_date = card.find('span', 'display-18 inline-flex').text.strip()
            
                if re.findall(r'[0-9]', posted_at_date):
                    posted_at_days = ''.join(re.findall(r'[0-9]', posted_at_date))    
                    post_date = (datetime.today() - timedelta(int(posted_at_days))).strftime('%d-%m-%Y')

                else:
                    post_date = datetime.today().strftime('%d-%m-%Y')

            except AttributeError:
                post_date = ''
            try:
                salary = card.find('span', 'salarytext').text.strip()
            except AttributeError:
                salary = ''
                
            try:
                url = 'https://www.jobmaster.co.il' + card.find('a', 'CardHeader').get('href')
            except AttributeError:
                url = '' 
         
            try:
                description = self.get_qualifactions(url)
            except AttributeError:
                description = []
            
            try:
                skills = self.get_skill_sets(description)
            except:
                skills = []
                
            job = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'date': post_date,     
                    'description': description,
                    'salary': salary,
                    'url': url,
                    'skills': skills
            }
            
            return job
        
    def extract_jobs_card_list(self, soup):
        return soup.find_all('article', 'CardStyle JobItem font14')
        
    def generate_url(self, job_title, job_location):
        return self.url_template.format(job_title, job_location)

    def get_skill_sets(self, qualifactions_list):
        
        skills = Skill.objects.all()

        skills_lowerd=[x.description.lower() for x in skills]  # convert list to lowercase to parse

        yo=[]
        
        for i in range(len(qualifactions_list)):
                    a=skills_lowerd
                    dd=[x for x in a if x in qualifactions_list[i].lower()]
                    if(len(dd) > 0):
                        for j in range(len(dd)):
                            if(dd[j] not in yo):
                                yo.append(dd[j])
                
        return yo;

    def find_next_page(self, soup):
        try:
            pagination =  self.soup.find(id='paging').find('a', string='הבא»')
            url = 'https://www.jobmaster.co.il' + pagination.get('href')
        except AttributeError:
            url = None
        
        return url

    def start(self, job_title, job_location):
        
        jobs_list = []
        url = self.generate_url('python', 'אשדוד+ואשקלון')
        
        while True:
            soup = self.request_from_indeed(url)
            
            if not soup:
                break
            job_cards = self.extract_jobs_card_list(soup)
            
            for job_card in job_cards:    
                job = self.extract_job_card_data(job_card)
                jobs_list.append(job)

            # save_jobs_to_database(jobs_list)

            sleep_for_random_interval()
            
            url = self.find_next_page(soup)
            
            if not url:
                break
            
        return jobs_list
                    
class IndeedScrapper:
    
    def __init__(self):
        self.url_template = "https://il.indeed.com/jobs?q={}&l={}"

    def request_from_indeed(self, url):
        
        scraper = cloudscraper.create_scraper()  
        response = scraper.get(url=url)
        
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            return None
    
    def get_skill_sets(self, qualifactions_list):
    
        skills = Skill.objects.all()

        skills_lowerd=[x.description.lower() for x in skills]  # convert list to lowercase to parse

        yo=[]
        
        for i in range(len(qualifactions_list)):
                    a=skills_lowerd
                    dd=[x for x in a if x in qualifactions_list[i].lower()]
                    if(len(dd) > 0):
                        for j in range(len(dd)):
                            if(dd[j] not in yo):
                                yo.append(dd[j])
                
        return yo;
 
    def get_qualifactions(self, url):
        
        qualifactions_list = []
        soup = self.request_from_indeed(url)
        
        try:
            qualifactions = soup.find('div',{'class':'jobsearch-jobDescriptionText'})
            
            if(qualifactions is None):
                qualifactions = soup.find('div',{'class':'jobSectionHeader'}).next_element

            
            for qualifaction in qualifactions:
                try:
                    qualifactions_list.append(''.join(qualifaction.text.strip()))
                except AttributeError:
                    qualifactions_list.append('')   
        except AttributeError:
            qualifactions_list = []
            
        return qualifactions_list


    def extract_job_from_card(self, card):
        atag = card.h2.a
        try:
            job_title = atag.span.get('title')
            
        except AttributeError:
            job_title = ''
        try:
            company = card.find('span', 'companyName').text.strip()
        except AttributeError:
            company = ''
        try:
            location = card.find('div', 'comapnyLocation').text.strip()
        except AttributeError:
            location = ''
      
        try:
            posted_at_date = card.find('span', attrs={'class': 'date'}).text.strip() 
            
            if re.findall(r'[0-9]', posted_at_date):
                posted_at_days = ''.join(re.findall(r'[0-9]', posted_at_date))    
                post_date = (datetime.today() - timedelta(int(posted_at_days))).strftime('%d-%m-%Y')
                
            else:
                post_date = datetime.today().strftime('%d-%m-%Y')

            
        except AttributeError:
            post_date = ''
        try:
            salary = card.find('span', 'salarytext').text.strip()
        except AttributeError:
            salary = ''
            
        url = 'https://il.indeed.com' + atag.get('href')
        
        print(url)
        try:
            description = self.get_qualifactions(url)
        except AttributeError:
            description = []
        
        
        try:
            skills = self.get_skill_sets(description)
        except:
            skills = []
            
        job = {
                'title': job_title,
                'company': company,
                'location': location,
                'date': post_date,     
                'description': description,
                'salary': salary,
                'url': url,
                'skills': skills
        }
      
            
        return job
    
    def extract_jobs_card_list(self, soup):
        return soup.find_all('div', 'job_seen_beacon')
        
    def generate_url(self, job_title, job_location):
        return self.url_template.format(job_title, job_location)

    def find_next_page(self, soup):
        try:
            pagination = soup.find("a", {"aria-label": "Next Page"}).get("href")
            url = "https://il.indeed.com" + pagination
        except AttributeError:
            url = None
        
        return url

    def start(self, job_title, job_location):
        jobs_list = []
        url = self.generate_url('python', 'ashdod')
        
        while True:
            soup = self.request_from_indeed(url)
            
            if not soup:
                break
            job_cards = self.extract_jobs_card_list(soup)
            
            for job_card in job_cards:    
                job = self.extract_job_from_card(job_card)
                jobs_list.append(job)
                
            # save_jobs_to_database(jobs_list)
            
            
            url = self.find_next_page(soup)
            
            
            sleep_for_random_interval()

            
            if not url:
                break
        
        return jobs_list

class DrushimScrapper:

    def __init__(self):
        self.url_template = "https://www.drushim.co.il/jobs/area/{}/?searchterm={}"

    def request_from_indeed(self, url):
        
        scraper = cloudscraper.create_scraper()  
        response = scraper.get(url=url)
        
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            return None
        
    def get_skill_sets(self, qualifactions_list):
        
        skills = Skill.objects.all()

        skills_lowerd=[x.description.lower() for x in skills]  # convert list to lowercase to parse

        yo=[]
        
        for i in range(len(qualifactions_list)):
                    a=skills_lowerd
                    dd=[x for x in a if x in qualifactions_list[i].lower()]
                    if(len(dd) > 0):
                        for j in range(len(dd)):
                            if(dd[j] not in yo):
                                yo.append(dd[j])
                
        return yo;
 
    def get_qualifactions(self, url):
        
        qualifactions_list = []
        soup = self.request_from_indeed(url)
        
        try:
            qualifactions = soup.find('div',{'class':'layout job-details-box vacancyFullDetails wrap'})
            
            if(qualifactions is None):
                qualifactions = []

            
            for qualifaction in qualifactions:
                try:
                    qualifactions_list.append(''.join(qualifaction.text.strip()))
                except AttributeError:
                    qualifactions_list.append('')   
        except AttributeError:
            qualifactions_list = []
            
        return qualifactions_list


    def extract_job_from_card(self, card):
            
            try:
                title = card.find('span', 'job-url').text.strip()
            except AttributeError:
                title= ''
            try:
                company = card.find('p', 'display-22 view-on-submit disabledLink pb-1 mb-0').text.replace('|',' ').strip()
            except AttributeError:
                company = ''
            try:
                location = card.find('div', 'flex nowrap flex-basis-0 flex-grow-0 ml-2').text.strip()
            except AttributeError:
                location = ''
            
            try:
                post_date = card.find('span', 'display-18 inline-flex').text.strip()
            except AttributeError:
                post_date = ''
            try:
                salary = card.find('span', 'salarytext').text.strip()
            except AttributeError:
                salary = ''
            
            try:
                url = 'https://www.drushim.co.il' + card.find('div', 'flex nowrap align-self-center pc-view open-job text-center').a.get('href')
            except AttributeError:
                url = ''
            
            try:
                description = self.get_qualifactions(url)
            except AttributeError:
                description = []
        
        
            try:
                skills = self.get_skill_sets(description)
            except:
                skills = []
            
            job = {
                'title': title,
                'company': company,
                'location': location,
                'date': post_date,     
                'description': description,
                'salary': salary,
                'url': url,
                'skills': skills
            }
            
            return job
             
    def extract_jobs_card_list(self, soup):
        return soup.find_all('div', 'job-item')
        
    def generate_url(self, job_title, job_location):
        return self.url_template.format(job_location, job_title)

    def find_next_page(self, soup):
        try:
            url = None
        except AttributeError:
            url = None
            
        return url

    
    def start(self, job_title, job_location):
        jobs_list = []
        url = self.generate_url('python', '1')
        
        while True:
            soup = self.request_from_indeed(url)
            
            if not soup:
                break
            
            job_cards = self.extract_jobs_card_list(soup)
            
            for job_card in job_cards:    
                job = self.extract_job_from_card(job_card)
                jobs_list.append(job)
                
            # save_jobs_to_database(jobs_list)
            
            sleep_for_random_interval()
            
            url = self.find_next_page(soup)
            
            
            sleep_for_random_interval()

            
            if not url:
                break
        
        return jobs_list

