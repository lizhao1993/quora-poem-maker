import pronouncing
import string
import os
import yaml
import random
import pickle
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, widgets
from flask_bootstrap import Bootstrap

DEBUG = True
app = Flask(__name__)
Bootstrap(app)


def syllable_count(sentence):
    phones = []
    for p in sentence.split():
        if not pronouncing.phones_for_word(p.strip()) == []:
            phones.append(pronouncing.phones_for_word(p.strip())[0])
        else:
            phones.append("")
    return sum([pronouncing.syllable_count(p) for p in phones])

def accepted(topics, accepted_topics = set(['Startups', "Technology",  
                                            "Software" "Engineering", "Computer", 
                                            "Computer Science", "San Francisco", 
                                            "Silicon Valley", "Venture",
                                            "Founder", "Entrepreneurship"])):
    for topic in accepted_topics:
        for current_topic in topics:
            if topic.lower() in current_topic.lower() or current_topic.lower() in topic.lower():
                return True
    return False

def load_questions():
    """load in the questions, outputs a dict of questions by syllable size"""
    questions = {}
    exclude = set(string.punctuation)
    with open('answered_data_10k.in') as data:
        real_data = data.readlines()[1:]
        for line in real_data:
            line = yaml.load(line)
            try:
                question = line['question_text']
                question_topics = [topic['name'] for topic in line['topics']]
                if not line['context_topic'] == None:
                    question_topics.append(line['context_topic']['name'])
                #if accepted(question_topics):
                question = ''.join(ch for ch in question if ch not in exclude)
                if syllable_count(question) in questions:
                    questions[syllable_count(question)].append(question)
                else:
                    questions[syllable_count(question)] = [question]
            except:
                print(line)
    return questions

def make_poem_lines(questions, num_of_couplets):
    """take in questions, make poem"""
    keys = list(questions.keys())
    #print(keys)
    poem = []
    found = False

    for index in range(0, len(keys)):
        #print("-----------------" + str(keys[index])+ "----------------------")
        same_length_poem = []
        if keys[index] > 3 and keys[index] < 12:
            same_length_questions = list(set(questions[keys[index]]))
            used = set()
            for i in range(0, len(same_length_questions)):
                a_question = same_length_questions[i]
                for j in range(i+1, len(same_length_questions)):
                    another_question = same_length_questions[j]
                    if a_question in used or another_question in used:
                        continue
                    if a_question.split()[-1] in pronouncing.rhymes(another_question.split()[-1]):
                        same_length_poem.append([a_question, another_question])
                        used.add(a_question)
                        used.add(another_question)
        if len(same_length_poem) > num_of_couplets:
            poem.append(same_length_poem)
    return poem

def random_sample(poem, num_of_couplets):
    if poem == []:
        return []
    sample = []
    rand_size = random.randrange(0, len(poem))
    same_size_poem = poem[rand_size]
    for i in range(0, num_of_couplets):
        rand_couplet = random.randrange(0, len(same_size_poem))
        couplet = same_size_poem[rand_couplet]
        sample.append(couplet)
        same_size_poem.remove(couplet)
    return sample

def format(sample):
    if sample == []:
        return ["Not enough questions for a poem, try lowering the number of couplets."]
    else:
        for line in sample:
            line[0] = line[0] + "?"
            line[1] = line[1] + "?"
        return sample

def write_poem():
    """making poems"""
    num_of_couplets = 4

    if os.path.isfile("saved_poems.pkl"):
        with open("saved_poems.pkl", 'rb') as saved_poems:
            poem = pickle.load(saved_poems)
    else:
        questions = load_questions()
        poem = make_poem_lines(questions, num_of_couplets)
        with open("saved_poems.pkl", 'wb') as saved_poems:
            pickle.dump(poem, saved_poems, -1)

    return format(random_sample(poem, num_of_couplets))


class MakePoemButton(Form):
    #label = 'Make me a Quora poem!'
    make_poem_button = widgets.SubmitInput()

@app.route('/', methods=['GET', 'POST'])
def make_poem():
    make_poem_button = MakePoemButton(request.form)
    if request.method == 'POST':
        sample = write_poem()
        if len(sample[0]) > 1:
            for line in sample:
                flash(line[0])
                flash(line[1])
        else:
            flash(sample[0][0])
    return render_template('make_poem.html', form=make_poem_button)

if __name__ == "__main__":
    app.run()

