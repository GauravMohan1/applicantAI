import os

import openai
from flask import Flask, redirect, render_template, request, url_for
import PyPDF2



app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    result = request.args.get("result")
    return render_template("index.html",result=result)

@app.route("/app", methods=["POST"])
def get_letter():
    company = request.form["company"]
    industry = request.form["industry"]
    resume = extract_resume()
    job_desc = extract_job()
    
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=generate_prompt(resume, company, job_desc, industry),
        temperature=0.8,
        max_tokens = 1500,
        n=2
    )

    cover_letter = response.choices[0].text
    return redirect(url_for("index", result=cover_letter))
   
def generate_prompt(resume,company, job_desc, industry):
    prompt = {'Finance': "The first paragraph should highlight why the company is interesting to the applicant based off what the company does, company culture, and the company's mission. The second paragraph should align the role responsibilities with the applicant's accomplishments. The third paragraph should mention the leadership abilities of the applicant and explain how that aligns with the company's mission and values.",
              'Business': "The first paragraph should highlight why the company is interesting to the applicant based off what the company does, company culture, and the company's mission. The second paragraph should highlight how the applicant's internship and professional experience aligns with the role qualifications. The third paragraph should talk about the applicant's communication and leadership skills and how that fits into to the role and company.",
              'Product': "The first paragraph should highlight why the company is interesting to the applicant based off what the company does, company culture, and the company's mission. The second paragraph should highlight the various products the applicant has worked on and his or her impact on improving the product and align these experiences with the company's product. The third paragraph should talk about the applicant's soft skills, such as communication, time management, and creativity and why that will help him or her succeed on the job.",
              'HR': "The first paragraph should highlight why the company is interesting to the applicant based off what the company does, company culture, and the company's mission. The second paragraph should highlight the applicant's initiative to help others through great communication and why that leadership is important in this role. The third paragraph should highlight the applicant's ability to resolve conflict and why that aligns wuth the role responsibilities and company values.",
              'Engineering': "The first paragraph should highlight why the company is interesting to the applicant based off what the company does, company culture, and the company's mission. The second paragraph should highlight the applicant's impact created from the projects he or she developed. The third paragraph should mention how the role responsibilities aligns with the applicant's skills and domain experience why this makes them a perfect fit for the company."}
    string = "Write a three paragraph cover letter for a job application using the information below."
    string += "\n"
    string += 'Company: ' + company.capitalize() + "\n"
    string += 'Resume: ' + resume + "\n"
    string += 'Job Description: ' + job_desc + "\n"
    string +=  prompt[industry]
    return string


def extract_resume():
    response_text = ''
    # Get the binary data of the PDF file from the request
    pdf_file = request.files['resume']

    # Create a PDF object
    pdf = PyPDF2.PdfReader(pdf_file)
    # Iterate over every page in the PDF
    text = ""
    for page in range(len(pdf.pages)):
        # Extract the text from the current page
        text += pdf.pages[page].extract_text()
    # Return the extracted text
# Apply text on GPT-3 Summarization
    response = openai.Completion.create(
                model="text-davinci-003",
                prompt="""Summarize the text below into a JSON with exactly the following structure {basic_info: {first_name, last_name, full_name, email, phone_number, location, portfolio_website_url, linkedin_url, github_main_page_url, university, education_level (BS, MS, or PhD), graduation_year, graduation_month, majors, GPA}, work_experience: [{job_title, company, location, duration, job_summary}], leadership_experience:[{role, description}], project_experience:[{project_name, project_discription}]}
""" + '\n' + text,
                temperature = 0.0,
                max_tokens = 1500
            )

    response_text += response['choices'][0]['text'].strip()

    return response_text


def extract_job():
    response_text = ''
    description = request.form['job']
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="""Summarize the text below into a JSON with exactly the following structure {basic_info: {company description}, role_description: [{job_title, responsibilities}], role_qualifications:[{qualifications}]}
""" + '\n' + description,
        temperature = 0.0,
        max_tokens = 1000
    )
    response_text += response['choices'][0]['text'].strip()

    return response_text

