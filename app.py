from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
import pandas
import re



app = Flask(__name__, static_folder='static')

@app.route('/')
def main():
    return render_template('index.html', title='LINE TALK ANALYSIS')

@app.route("/templates", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/',methods=['POST'])
def post():
    input_text = request.files['file1']
    user1_len, user2_len, user1, user2 =  get_result(input_text)
    return render_template('result.html', user1_len=user1_len, user2_len=user2_len, user1=user1, user2=user2)

@app.route("/result.html", methods=["GET"])
def nextpage():
    return render_template("result.html")

def get_result(input_text):
    line_df = pandas.read_csv(input_text, sep='\n')

    line_df = line_df.rename(columns={line_df.columns[0]:'talks'})
    line_df = line_df[1:]

    # 正規表現でトークから日付を取得し新しいカラムとして結合する
    date_list = []
    date_pattern = '(\d+)/(\d+)/\d+\(.?\)'
    for talk in line_df['talks']:
        result = re.match(date_pattern, talk)
        if result:
            date_t = result.group()
            date_list.append(date_t)
        else:
            date_list.append(date_t)
    line_df['date'] = date_list

    flag = line_df['talks'].isin(line_df['date'])
    line_df = line_df[~flag]
    line_df.dropna(inplace=True)   

    time_l = []
    user_l = []
    talk_l = []
    date_l = []
    count = 0
    for date, talk in zip(line_df['date'], line_df['talks']):
        # もし正規表現で時間が取れたらスプリットして3つに分ける
        if(re.match('(\d+):(\d+)', talk)):
            try:
                if(len(talk.split('\t')[0]) == 5):
                    date_l.append(date)
                    time_l.append(talk.split('\t')[0])
                    user_l.append(talk.split('\t')[1])
                    talk_l.append(talk.split('\t')[2])
                    count = count + 1
                else:
                    continue
            except:
                talk_l.append("メッセージの送信取り消し")
                count = count + 1
        else:
            talk_l[count-1] = talk_l[count-1] + talk
            
    # if(user_l != date_l):
    #     user_l.append(user1)
            
    line_df = pandas.DataFrame({"date" : date_l,
                            "time" : time_l,
                            "user" : user_l,
                            "talk" : talk_l})

    user1 = line_df['user'].unique()[0]
    user2 = line_df['user'].unique()[1]

    user1_len = len(line_df[line_df['user']==user1])
    user2_len = len(line_df[line_df['user']==user2])

    return user1_len, user2_len, user1, user2

if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run(debug=True,host="127.0.0.1" ,port=8085)