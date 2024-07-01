import os
import re
import analyzer
from patternitem import PatternItem

class Dictionary(object):
    """ランダム辞書とパターン辞書のデータをインスタンス変数に格納する

    Attributes:
        random(strのlist):
            ランダム辞書の全ての応答メッセージを要素として格納
            [メッセージ１,メッセージ２,メッセージ３, ・・・]

        pattern(PatternItemのlist):
            [PatternItem1 , PatternItem2, PatternItem3, ・・・]
    """
    def __init__(self):
        self.random =  self.make_random_list()
        self.pattern = self.make_pattern_dictionary()
        self.template = self.make_template_dictionary()

    def make_random_list(self):
        path = os.path.join(os.path.dirname(__file__), 'dics', 'random.txt')
        rfile = open(path, 'r', encoding = 'utf_8')
        r_lines = rfile.readlines()
        rfile.close()
        random_list = []
        for line in r_lines:
            str = line.rstrip('\n')
            if (str!=''):
                random_list.append(str)
                
        return random_list
    
    def make_pattern_dictionary(self):
        path = os.path.join(os.path.dirname(__file__), 'dics', 'pattern.txt')
        pfile = open(path, 'r', encoding = 'utf_8')
        p_lines = pfile.readlines()
        print(p_lines)
        pfile.close()
        pattern_list = []
        for line in p_lines:
            str = line.rstrip('\n')
            if (str!=''):
                pattern_list.append(str)

        patternitem_list = []
        for line in pattern_list:
            ptn, prs = line.split('    ')
            patternitem_list.append(PatternItem(ptn, prs))
        return patternitem_list
    
    def make_template_dictionary(self):
        """テンプレート辞書ファイルから辞書オブジェクトのリストを作る

        Returns:(dict):
            {'空欄の数': [テンプレート１,テンプレート２,・・・],・・・}
        """

        path = os.path.join(os.path.dirname(__file__), 'dics', 'template.txt')
        tfile = open(path, 'r', encoding = 'utf_8')
        t_lines = tfile.readlines()
        tfile.close()

        new_t_lines = []
        for line in t_lines:
            str = line.rstrip('\n')
            if (str!=''):
                new_t_lines.append(str)

        template_dictionary = {}
        for line in new_t_lines:
            count, tempstr = line.split('\t')
            if not count in template_dictionary:
                template_dictionary[count] = []
            template_dictionary[count].append(tempstr)

        return template_dictionary
    
    def study(self, input, parts):
        """ユーザーの発言を学習する

        Args:
            input (str): ユーザーの発言
            parts (strの多重list):
                ユーザー発言の形態素解析結果
                例：[['わたし','名詞,代名詞,一般,*'],
                    ['は','助詞,係助詞,*,*'],・・・]
        """
        input = input.rstrip('\n')
        self.study_random(input)
        self.study_pattern(input, parts)
        self.study_template(parts)

    def study_random(self, input):
        """ユーザーの発言をランダム辞書に書き込む

        Args:
            input (str): ユーザーの発言
        """
        #ユーザーの発言がランダム辞書に存在しなければself.randomの末尾に追加
        if not input in self.random:
            self.random.append(input)

    def study_pattern(self, input, parts):
        """ユーザーの発言を学習し、パターン辞書への書き込みを行う

        Args:
            input (str): ユーザーの発言 
            parts (strの多重list):形態素解析結果の多重リスト 
        """
        #ユーザー発言の形態素の品詞情報がkeyword_check()で指定した品詞と一致するか、繰り返しパターンマッチを試みる
        #
        # Block Parameters:
        #   word(str): ユーザー発言の形態素
        #   part(str): ユーザー発言の形態素の品詞情報
        for word, part in parts:
            #形態素の品詞情報が指定の品詞にマッチしたときの処理
            if analyzer.keyword_check(part):
                # PatternItemオブジェクトを保持するローカル変数
                depend = None
                for ptn_item in self.pattern:
                    if re.search(
                        ptn_item.pattern,
                        word
                        ):
                        depend = ptn_item
                        break
                if depend:
                    depend.add_phrase(input) # 引数はユーザー発言
                else:
                    self.pattern.append(
                        PatternItem(word, input)
                        )
    
    def study_template(self, parts):
        """ユーザーの発言を学習し、テンプレート辞書オブジェクトに登録する

        Args:
            parts (strのlistを格納したlist): ユーザーメッセージの解析結果
        """
        tempstr = ''
        count = 0

        ##ユーザーメッセージの形態素が名詞であれば形態素を%noun%に書き換え、
        ##そうでなければ元の形態素のままにして、「やっぱり%noun%だよね」のような
        ##パターン文字列を作る

        for word, part in parts:
            if (analyzer.keyword_check(part)):
                word = '%noun%'
                count += 1
            tempstr += word

        if count > 0:
            count = str(count)
            if not count in self.template:
                self.template[count] = []

            if not tempstr in self.template[count]:
                self.template[count].append(tempstr)

    def save(self):
        """ self.randomの内容でランダム辞書ファイルを更新する

        """
        for index, element in enumerate(self.random):
            self.random[index] = element +'\n'
        path = os.path.join(os.path.dirname(__file__), 'dics', 'random.txt')
        with open(path, 'w', encoding = 'utf_8') as f:
            f.writelines(self.random)

        #パターン辞書ファイルに書き込むデータを保持するリスト
        pattern = []
        # パターン辞書の全てのPatternItemオブジェクトから辞書ファイル1行のフォーマットを繰り返し作成する
        for ptn_item in self.pattern:
            pattern.append(ptn_item.make_line() + '\n')
        path = os.path.join(os.path.dirname(__file__), 'dics', 'pattern.txt')
        with open(path, 'w', encoding = 'utf_8') as f:
            f.writelines(pattern)

        #テンプレート辞書ファイルに書き込むデータを保持するリスト
        templist = []
        #'%noun%'の出現回数[TAB]テンプレート\nの1行を作り、
        #'%noun%'の出現回数ごとにリストをまとめる
        # Block Parameters:
        #   key(str):テンプレートのキー('%noun%'の出現回数) 
        #   val(str):テンプレートのリスト
        for key, val in self.template.items():
            #同一のkeyの値で、''%noun%'の出現回数[TAB]テンプレート\n'の1行を作る
            # Block Parameter:
            #   v(str):テンプレート１個
            for v in val:
                templist.append(key + '\t' + v + '\n')
        #リスト内のテンプレートをソート
        templist.sort()
        path = os.path.join(os.path.dirname(__file__), 'dics', 'template.txt')
        with open(path, 'w', encoding = 'utf_8') as f:
            f.writelines(templist)


    
    

    

