import sqlite3


def get_db():
    con = sqlite3.connect('prompts_db.sqlite')
    return con

def show_entries():
    con = get_db()
    cur = con.cursor()
    cur.execute('select * from PROMPTS')

    for row in cur.fetchall():
        print(row)
    
def add_prompt(prompt_text):
    con = get_db()
    cur = con.cursor()
    cur.execute("insert into PROMPTS(PROMPT_TEXT) values (?)", (prompt_text,))
    con.commit()
    #show_entries()

def add_prompt_usage(prompt_id):
    con = get_db()
    cur = con.cursor()
    cur.execute("update PROMPTS set P_USAGES = P_USAGES+1 WHERE P_ID = (?)", (prompt_id,))
    con.commit()
    #show_entries()



def get_prompt_id_from_text(prompt_text):
    # SELECT P_ID FROM PROMPTS WHERE PROMPT_TEXT = "Hier ist ein Prompt"
    con = get_db()
    cur = con.cursor()
    cur.execute("select P_ID from PROMPTS where PROMPT_TEXT = (?)", (prompt_text,))
    return cur.fetchall()[0][0]


# SELECT PROMPT_TEXT FROM PROMPTS ORDER BY P_USAGES ASC LIMIT 1
def get_prompts_by_usages(how_many_prompts, add_usages_automatically):
    con = get_db()
    cur = con.cursor()
    cur.execute("select PROMPT_TEXT from PROMPTS order by P_USAGES asc limit (?)", (how_many_prompts,))
    
    list_to_return = []

    for row in cur.fetchall():
        list_to_return.append(row[0])
        if (add_usages_automatically):
            add_prompt_usage(get_prompt_id_from_text(row[0]))
    
    return list_to_return


def read_prompts_into_list(filename):
    lineList = [line.rstrip('\n') for line in open(filename)]
    return lineList
    # for l in lineList:
    # print(l)



#show_entries()
#add_prompt_usage(3)
#print(get_prompts_by_usages(3, True))

""" for prompt in read_prompts_into_list("samplePrompts.txt"):
    add_prompt(prompt.strip())
 """

# show_entries()
