import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense
import numpy as np
import json

# Tải dữ liệu huấn luyện
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

questions = [item['question'] for item in data]
answers = ['<start> ' + item['answer'] + ' <end>' for item in data]

# Tokenizer
tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='')
tokenizer.fit_on_texts(questions + answers)
question_sequences = tokenizer.texts_to_sequences(questions)
answer_sequences = tokenizer.texts_to_sequences(answers)
maxlen = max(max(len(seq) for seq in question_sequences), max(len(seq) for seq in answer_sequences))

question_sequences = tf.keras.preprocessing.sequence.pad_sequences(question_sequences, maxlen=maxlen, padding='post')
answer_sequences = tf.keras.preprocessing.sequence.pad_sequences(answer_sequences, maxlen=maxlen, padding='post')

# Bộ giải mã đầu vào và đầu ra
decoder_input_data = answer_sequences[:, :-1]
decoder_target_data = answer_sequences[:, 1:]

# Tạo mô hình
latent_dim = 256
encoder_inputs = Input(shape=(None,))
encoder_embedding = tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=latent_dim)(encoder_inputs)
encoder_lstm = LSTM(latent_dim, return_state=True)
encoder_outputs, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(None,))
decoder_embedding = tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=latent_dim)(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(len(tokenizer.word_index) + 1, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')

model.fit([question_sequences, decoder_input_data], decoder_target_data, epochs=50)

model.save('chatbot_model.h5')
tokenizer_json = tokenizer.to_json()
with open('tokenizer.json', 'w', encoding='utf-8') as file:
    file.write(tokenizer_json)
