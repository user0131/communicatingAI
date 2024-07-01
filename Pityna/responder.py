import random
import re
import analyzer

class Responder(object):
    def __init__(self, name):
        self.name = name

    def response(self, input, parts):
        return ''
    
class RepeatResponder(Responder):
    def __init__(self, name):
        super().__init__(name)

    def response(self, input, mood, parts):
        return '{}ってなに？'.format(input)
    
class RandomResponder(Responder):
    def __init__(self, name, dic_random):
        super().__init__(name)
        self.random = dic_random

    def response(self, input, mood, parts):
        return random.choice(self.random)
    
class PatternResponder(Responder):
    def __init__(self, name, dic_pattern, dic_random):
        super().__init__(name)
        self.pattern = dic_pattern
        self.random = dic_random

    def response(self, input, mood, parts):
        resp = None
        for ptn_item in self.pattern:
            m = ptn_item.match(input)
            if m:
                resp = ptn_item.choice(mood)
            if resp != None:
                return re.sub('%match%', m.group(), resp)
        return random.choice(self.random)
    
class TemplateResponder(Responder):
    """ テンプレートに反応するためのサブクラス
    
    Attributes:
        template (dict): 要素は{ '%noun%の出現回数' : [テンプレートのリスト] } 
        random(list): 要素はランダム辞書の応答フレーズ群
    """
    def __init__(self, name, dic_template, dic_random):
        """ スーパークラスの__init__()にnameを渡し、
            テンプレート辞書とランダム辞書をインスタンス変数に格納する
        
        Args:
            name(str): Responderオブジェクトの名前。            
            dic_template(dic): Dictionaryが保持するテンプレート辞書
            dic_random(list): Dictionaryが保持するランダム辞書
        """
        super().__init__(name)
        self.template = dic_template
        self.random = dic_random
        
    def response(self, input, mood, parts):
        """ テンプレートを使用して応答フレーズを生成する

        Args:
            input(str): ユーザーの発言
            mood(int): ピティナの機嫌値
            parts(strのlist): ユーザー発言の解析結果

        Returns:str:
            パターンにマッチした場合はパターンと対になっている応答フレーズを返す
            パターンマッチしない場合はランダム辞書から返す            
        """
        # ユーザー発言の名詞の部分のみを保持するリスト
        keywords = []
        # 解析結果partsの「文字列」→word、「品詞情報」→partに順次格納
        #
        # Block Parameters:
        #   word(str): ユーザー発言の形態素
        #   part(str): 形態素の品詞情報
        for word, part in parts:
            # 名詞であれば形態素をkeywordsに追加
            if analyzer.keyword_check(part):
                keywords.append(word)
        # keywordsに格納された名詞の数を取得
        count = len(keywords)
        # keywordsリストに1つ以上の名詞が存在し、
        # 名詞の数に対応する'%noun%'を持つテンプレートが存在すれば
        # テンプレートを利用して応答フレーズを生成する
        if (count > 0) and (str(count) in self.template): 
            # テンプレートリストからランダムに1個抽出
            resp = random.choice(
                self.template[str(count)]
                )
            # keywordsから取り出した名詞でテンプレートの%noun%を書き換える
            for word in keywords:
                resp = resp.replace(
                    '%noun%', # 書き換える文字列
                    word,     # 書き換え後の文字列
                    1         # 書き換える回数
                    )
            return resp
        # ユーザー発言に名詞が存在しない、または適切なテンプレートが
        # 存在しない場合はランダム辞書から返す
        return random.choice(self.random)
    