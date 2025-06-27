from flask import Flask, render_template, request, jsonify, send_from_directory
import onnxruntime as ort
import numpy as np
import cv2, os, hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ——— ONNXRuntime 加载模型 ———
onnx_path = os.path.join(BASE_DIR, 'FB_demo.onnx')
session = ort.InferenceSession(onnx_path)
# 打印一下确保加载正确
print(">> Loaded ONNX model sha256:",
      hashlib.sha256(open(onnx_path,'rb').read()).hexdigest())

# 假设你的模型输入是 (1, C, H, W)，输出为 logits or probabilities
def run_inference(img_path):
    img = cv2.imread(img_path)
    # TODO: 按你的 SimpleCNN 训练时的预处理做 resize / normalize
    img = cv2.resize(img, (64, 64))           # 例：调整为 64×64
    img = img.astype(np.float32) / 255.0      # 例：归一化
    img = np.transpose(img, (2,0,1))          # HWC → CHW
    inp = img[np.newaxis, ...]                # 批次维度 (1,C,H,W)
    outputs = session.run(None, {session.get_inputs()[0].name: inp})
    return outputs[0]  # 根据你的输出格式调整

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            file = request.files['image']
            img_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(img_path)

            # —— 调用推理 —— 
            preds = run_inference(img_path)
            # TODO: 根据 preds 画框或写文字，这里做个简单示例
            img = cv2.imread(img_path)
            label = np.argmax(preds, axis=1)[0]
            cv2.putText(img, f"Class: {label}", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            out_path = os.path.join(OUTPUT_FOLDER, file.filename)
            cv2.imwrite(out_path, img)
            return send_from_directory(OUTPUT_FOLDER, file.filename,
                                       mimetype='image/jpeg')
        except Exception as e:
            app.logger.error("Inference error", exc_info=e)
            return jsonify({'error': str(e)}), 500

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
