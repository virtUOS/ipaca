from transformers import AutoModelWithLMHead, AutoTokenizer


class NLP_Model():

    tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")
    model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")

    def __int__(self):
        print('sttart init')

    def get_question(self, answer, context, max_length=64):
        input_text = "answer: %s  context: %s </s>" % (answer, context)
        features = NLP_Model.tokenizer([input_text], return_tensors='pt')

        output = NLP_Model.model.generate(input_ids=features['input_ids'],
                                     attention_mask=features['attention_mask'],
                                     max_length=max_length)

        return NLP_Model.tokenizer.decode(output[0])


