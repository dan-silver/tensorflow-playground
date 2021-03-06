# Reported and fixed in TensorFlow
# https://github.com/tensorflow/tensorflow/issues/441

import tensorflow as tf

images = tf.Variable(tf.truncated_normal([10, 48, 48, 1], stddev=0.1))

tf.image_summary("max_images_bug_no_param", images) # 3 images displayed

tf.image_summary("max_images_bug_none_param", images, max_images=None) # 3 images displayed

tf.image_summary("max_images_bug_100_param", images, max_images=100) # 10 images displayed

with tf.Session() as sess:
    sess.run(tf.initialize_all_variables())
    summary_op = tf.merge_all_summaries()
    writer = tf.train.SummaryWriter('max_images_bug')
    summary_str = sess.run(summary_op)
    writer.add_summary(summary_str, 0)