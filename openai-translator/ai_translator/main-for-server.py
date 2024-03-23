import sys
import os
import gradio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, jsonify, request, send_file
from utils import ArgumentParser, ConfigLoader, LOG

from model import GLMModel, OpenAIModel, AzureOpenAIModel
from translator import PDFTranslator

"""
使用gradio实现图形化界面
"""
app = Flask(__name__)
TEMP_FILE_DIR = "temps_file/"


def translation(input_file, source_language, target_language):
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']

    if args.model_type == 'OpenAIModel':
        model = OpenAIModel(model=model_name, api_key=api_key)
    else:
        model = AzureOpenAIModel(model=model_name, api_key=api_key)

    pdf_file_path = input_file
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    print(f"pdf_file_path=={pdf_file_path}")
    output_file = translator.translate_pdf(pdf_file_path, file_format, target_language=target_language)
    return output_file


@app.route('/translation-pdf', methods=['POST'])
def translation_pdf():
    try:
        # 从request中获取 待翻译的文件以及源语言和目标语言
        input_file = request.files['input_file']
        source_language = request.form.get('source_language', '英语')
        target_language = request.form.get('target_language', '中文')

        LOG.info(f"input_file={input_file}---source_language={source_language}---target_language={target_language}")
        file_name = input_file.filename

        if input_file and file_name:
            input_file_path = TEMP_FILE_DIR + file_name
            input_file.save(input_file_path)
            output_file_path = translation(input_file_path, source_language, target_language)
            output_file_path = os.getcwd() + "/" + output_file_path
            # 返回翻译后的文件
            return send_file(output_file_path, as_attachment=True)
        else:
            response = {
                "status": "error",
                "message": "input_file is None"
            }
            return jsonify(response), 400
    except Exception as e:
        LOG.error(e)
        response = {
            "status": "error",
            "message": e.__str__()
        }
        return jsonify(response), 400


if __name__ == "__main__":
    app.run(debug=True)
