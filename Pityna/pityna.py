import responder
import random
import dictionary
import analyzer

class Pityna(object):
    """ピティナの本体クラス

    Attributes:
        name (str): Pitynaオブジェクトの名前を保持
        dictionary (obj: 'Dictionary'): Dictionaryオブジェクトを保持
        res_repeat (obj: 'RepeatResponder'): RepeatResponderオブジェクトを保持
        res_random (obj: 'RandomResponder'): RandomResponderオブジェクトを保持
        res_pattern (obj: 'PatternResponder'): PatternResponderオブジェクトを保持 
    """
    def __init__(self, name):
        self.name = name
        self.dictionary = dictionary.Dictionary()
        self.emotion = Emotion(self.dictionary.pattern)
        self.res_repeat = responder.RepeatResponder('Repeat?')
        self.res_random = responder.RandomResponder(
            'Random', self.dictionary.random)
        #PatternResponderを生成
        self.res_pattern = responder.PatternResponder(
            'Pattern', 
            self.dictionary.pattern,  # パターン辞書
            self.dictionary.random    # ランダム辞書
            )
        # TemplateResponderを生成
        self.res_template = responder.TemplateResponder(
                'Template',
                self.dictionary.template, # テンプレート辞書
                self.dictionary.random    # ランダム辞書
                )

    def dialogue(self, input):
        #ピティナの機嫌値を更新する
        self.emotion.update(input)
        #ユーザーの発言を解析。解析結果の多重リストをpartsに代入
        parts = analyzer.analyze(input)
        #1-100の数値をランダムに生成
        x = random.randint(1, 100)
        # 40以下ならPatternResponderオブジェクトにする
        if x <= 40:
            self.responder = self.res_pattern
        # 41～70以下ならTemplateResponderオブジェクトにする
        elif 41 <= x <= 70:
            self.responder = self.res_template
        # 71～90以下ならRandomResponderオブジェクトにする
        elif 71 <= x <= 90:
            self.responder = self.res_random
        # それ以外はRepeatResponderオブジェクトにする
        else:
            self.responder = self.res_repeat

        # 応答フレーズを生成
        resp = self.responder.response(
            input,             # ユーザーの発言
            self.emotion.mood, # ピティナの機嫌値
            parts              # ユーザー発言の解析結果
            )
        
        print(self.emotion.mood)
        #学習メソッドを呼ぶ
        self.dictionary.study(input, parts)
        #応答フレーズを返す
        return resp
    
    def save(self):
        """ Dictionaryのsave()を呼ぶ中継メゾット

        """
        self.dictionary.save()
    
    def get_responder_name(self):
        """応答に使用されたオブジェクト名を返す

        """
        return self.responder.name
    
    def get_name(self):
        """ Pitynaオブジェクトの名前を返す

        Returns:
            str: Pitynaクラスの名前
        """
        return self.name
    
class Emotion:
    """Pitynaの感情モデル

    Attributes:
        pattern (PatternItemのlist): [PatternItem1, PatternItem2, PatternItem3, ・・・]
        mood (int): ピティナの機嫌値を保持
    """
    MOOD_MIN = -15 
    MOOD_MAX = 15
    MOOD_RECOVERY = 0.5

    def __init__(self, pattern):
        # Dictonaryオブジェクトのpatternをインスタンス変数patternに格納
        self.pattern = pattern
        self.mood = 0

    def update(self, input):
        if self.mood < 0:
            self.mood += Emotion.MOOD_RECOVERY
        elif self.mood > 0:
            self.mood -= Emotion.MOOD_RECOVERY

        for ptn_item in self.pattern:
            if ptn_item.match(input):
                self.adjust_mood(ptn_item.modify)
                break

    def adjust_mood(self, val):
        """機嫌値を増減させるメゾット

        Args:
            val (int): 機嫌変動値modifyを格納
        """
        self.mood += int(val)
        if self.mood > Emotion.MOOD_MAX:
            self.mood = Emotion.MOOD_MAX
        elif self.mood < Emotion.MOOD_MIN:
            self.mood = Emotion.MOOD_MIN