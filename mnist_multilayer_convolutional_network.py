import mnist_data
import tensorflow as tf

# based on tutorial at http://www.tensorflow.org/tutorials/mnist/pros/index.html

mnist = mnist_data.read_data_sets('MNIST_data', one_hot=True)

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

# Helper method for maximum pooling. strides 2x2, 75% reduction in image size per pooling operation
def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')

x = tf.placeholder("float", shape=[None, 784], name="x") # None means the batch size can be any length
y_ = tf.placeholder("float", shape=[None, 10], name="y_") # One-hot 10-dimensional vector indicating which digit class the corresponding MNIST image belongs to




L2_SIZE = 64
L3_SIZE = 128
L3_PATCH_SIZE = 3

visualize_weights = False
visualize_filters = [3, 4, 5, 6] #indices of the h_conv1 layer to save as images. Empty array means no visualization of the filters



# Reshape input vector of size 784 to 28x28 array so the NN can use locality as a reference
x_image = tf.reshape(x, [-1,28,28,1]) #the second and third dimensions correspond to image width and height, and the final dimension corresponding to the number of color channels

# First Convolutional Layer

W_conv1 = weight_variable([7, 7, 1, 32]) # patch size (x,y), then number of input channels, then number of output channels
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)


channels = 32
img_size = 28



def visualize_filter(index):
  # Take only convolutions of image at index, discard convolutions for other images.
  V = tf.slice(h_conv1, (index, 0, 0, 0), (1, -1, -1, -1))
  V = tf.reshape(V, (img_size, img_size, channels))

  # Reorder so the channels are in the first dimension, x and y follow.
  V = tf.transpose(V, (2, 0, 1))
  # Bring into shape expected by image_summary
  V = tf.reshape(V, (-1, img_size, img_size, 1))

  tf.image_summary("first_conv_filter_" + str(index), V)


# Visualize the image convolutions on the first layer
[visualize_filter(i) for i in visualize_filters]



# Visualize the first convolution layer weights

L1_filter_size = 7
L1_num_filters = 32

print W_conv1.get_shape() # TensorShape([Dimension(7), Dimension(7), Dimension(1), Dimension(32)])


V1 = tf.reshape(W_conv1, (L1_filter_size, L1_filter_size, L1_num_filters))

# Reorder so the filters are in the first dimension, x and y follow.
V1 = tf.transpose(V1, (2, 0, 1))

# Bring into shape expected by image_summary
V1 = tf.reshape(V1, (L1_num_filters, L1_filter_size, L1_filter_size, 1))
print V1.get_shape() # TensorShape([Dimension(32), Dimension(7), Dimension(7), Dimension(1)])

if visualize_weights:
  tf.image_summary("weights", V1, max_images=L1_num_filters)





# Second Convolution Layer

W_conv15 = weight_variable([5, 5, 32, L2_SIZE]) # patch size (x,y), then number of input channels, then number of output channels
b_conv15 = bias_variable([L2_SIZE])
h_conv15 = tf.nn.relu(conv2d(h_pool1, W_conv15) + b_conv15)
h_pool15 = max_pool_2x2(h_conv15)

# Third Convolutional Layer

W_conv2 = weight_variable([L3_PATCH_SIZE, L3_PATCH_SIZE, L2_SIZE, L3_SIZE]) # patch size (x,y), then number of input channels, then number of output channels
b_conv2 = bias_variable([L3_SIZE])
h_conv2 = tf.nn.relu(conv2d(h_pool15, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)


# Densely Connected Layer

W_fc1 = weight_variable([4 * 4 * L3_SIZE, 1024]) # 4 = FLOOR(7/2)
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 4*4*L3_SIZE])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)


# Dropout

keep_prob = tf.placeholder("float", name="keep_prob")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)


# Readout Layer
# Convert to 10D vector for output

W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

# Train and Evaluate the Model

cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
tf.scalar_summary("cross_entropy", cross_entropy)

train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))

accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
tf.scalar_summary("train accuracy", accuracy)
# tf.image_summary("images", x_image, max_images=50)

# Add ops to save and restore all the variables.
saver = tf.train.Saver()

with tf.Session() as sess:
    # Create a dataset in TensorBoard to access this training run
    summary_op  = tf.merge_all_summaries()
    summary_writer = tf.train.SummaryWriter('data2')

    # For variables, random and constant, fill in their values
    # For normal vectors, such as weight_variable, assign a normal distribution in this step
    sess.run(tf.initialize_all_variables())

    for i in range(4501):
      batch = mnist.train.next_batch(50)
      # Only every 125 training runs, test the current accuracy on the current *training* batch 
      if i%1000 == 0:
        feed_dict = {x:batch[0], y_: batch[1], keep_prob: 1.0}
        train_accuracy = accuracy.eval(feed_dict=feed_dict)
        summary_str = sess.run(summary_op, feed_dict)
        summary_writer.add_summary(summary_str, i)
        print "step %d, training accuracy %g"%(i, train_accuracy)

      # Always train on each step [0,4501]
      train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})


    print W_conv1.eval()
    summary_writer.add_graph(sess.graph_def)
    print "test accuracy %g"%accuracy.eval(feed_dict={
        x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})

    # Save the variables to disk.
    save_path = saver.save(sess, "/tmp/model.ckpt")
    print "Model saved in file: ", save_path



'''

Sample output:

step 0, training accuracy 0.1
step 500, training accuracy 0.92
step 1000, training accuracy 0.98
step 1500, training accuracy 1
step 2000, training accuracy 0.96
step 2500, training accuracy 0.98
step 3000, training accuracy 0.98
step 3500, training accuracy 1
step 4000, training accuracy 1
step 4500, training accuracy 1
test accuracy 0.9894


'''