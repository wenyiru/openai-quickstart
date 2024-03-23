import sys
import os
import gradio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tempfile
from utils import ArgumentParser, ConfigLoader, LOG
import shutil

from model import GLMModel, OpenAIModel, AzureOpenAIModel
from translator import PDFTranslator

"""
使用gradio实现图形化界面
"""


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
    output_file = translator.translate_pdf(pdf_file_path, file_format, target_language=target_language)
    return output_file


def upload_file(file_obj, source_language, target_language):
    global tmp_dir
    print('临时文件夹地址：{}'.format(tmp_dir))
    print('上传文件的地址：{}'.format(file_obj.name))  # 输出上传后的文件在gradio中保存的绝对地址
    return translation(file_obj.name, source_language, target_language)


def main():
    global tmp_dir
    with tempfile.TemporaryDirectory(dir='.') as tmp_dir:
        # 定义输入和输出
        inputs = [
            gradio.components.File(label="上传待翻译的pdf文件"),
            gradio.Dropdown(["英语", "中文", "日语"], label="源语言", value="英语"),
            gradio.Dropdown(["英语", "中文", "日语"], label="目标语言", value="中文"),
        ]
        outputs = gradio.components.File(label="下载翻译后的pdf文件")
        # 创建 Gradio 应用程序
        app = gradio.Interface(fn=upload_file, inputs=inputs, outputs=outputs, title="AI翻译官",
                               description="上传待翻译的pdf文件，点击提交，即可下载翻译后的pdf文件",
                               # description="上传待翻译的pdf文件，选择翻译模型，点击提交，即可下载翻译后的pdf文件",
                               )
        # 启动应用程序
        app.launch(share=True)


if __name__ == "__main__":
    main()
