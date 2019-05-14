-- explain
WITH aaaa as (select 0::int as ii, 0::float4 as rr, wt.* from widedeep_train wt limit 100000000000),
     bbbb as (select 1::int as ii, 0::float4 as rr, wt.* from widedeep_test wt limit 100000000000) 
select 
dg_utils.transducer_column_int4(1) as nth,
dg_utils.transducer_column_float4(2) as accuracy,
dg_utils.transducer($PHI$PhiExec python2
import vitessedata.phi
vitessedata.phi.DeclareTypes('''
// 
// BEGIN INPUT TYPES
// tf_aux_ii int32
// tf_aux_rr float32
// age float32
// workclass string
// fnlwgt float32
// education string
// education_num float32
// marital_status string
// occupation string
// relationship string
// race string
// gender string
// capital_gain float32
// capital_loss float32
// hours_per_week float32
// native_country string
// income string
// END INPUT TYPES
//
// BEGIN OUTPUT TYPES
// round int32
// accuracy float32
// END OUTPUT TYPES
//
''')

# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Example code for TensorFlow Wide & Deep Tutorial using tf.estimator API."""

import argparse
import shutil
import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

_CSV_COLUMNS = [
    'age', 'workclass', 'fnlwgt', 'education', 'education_num',
    'marital_status', 'occupation', 'relationship', 'race', 'gender',
    'capital_gain', 'capital_loss', 'hours_per_week', 'native_country', 'income_bracket'
]

parser = argparse.ArgumentParser()

parser.add_argument(
    '--model_dir', type=str, default='/tmp/census_model',
    help='Base directory for the model.')

parser.add_argument(
    '--model_type', type=str, default='wide_deep',
    help="Valid model types: {'wide', 'deep', 'wide_deep'}.")

parser.add_argument(
    '--train_epochs', type=int, default=4, help='Number of training epochs.')

parser.add_argument(
    '--epochs_per_eval', type=int, default=2,
    help='The number of training epochs to run between evaluations.')

parser.add_argument(
    '--batch_size', type=int, default=100, help='Number of examples per batch.')

parser.add_argument(
    '--train_data', type=str, default='/tmp/census_data/adult.data',
    help='Path to the training data.')

parser.add_argument(
    '--test_data', type=str, default='/tmp/census_data/adult.test',
    help='Path to the test data.')

def build_model_columns():
  """Builds a set of wide and deep feature columns."""
  # Continuous columns
  age = tf.feature_column.numeric_column('age')
  education_num = tf.feature_column.numeric_column('education_num')
  capital_gain = tf.feature_column.numeric_column('capital_gain')
  capital_loss = tf.feature_column.numeric_column('capital_loss')
  hours_per_week = tf.feature_column.numeric_column('hours_per_week')

  education = tf.feature_column.categorical_column_with_vocabulary_list(
      'education', [
          'Bachelors', 'HS-grad', '11th', 'Masters', '9th', 'Some-college',
          'Assoc-acdm', 'Assoc-voc', '7th-8th', 'Doctorate', 'Prof-school',
          '5th-6th', '10th', '1st-4th', 'Preschool', '12th'])

  marital_status = tf.feature_column.categorical_column_with_vocabulary_list(
      'marital_status', [
          'Married-civ-spouse', 'Divorced', 'Married-spouse-absent',
          'Never-married', 'Separated', 'Married-AF-spouse', 'Widowed'])

  relationship = tf.feature_column.categorical_column_with_vocabulary_list(
      'relationship', [
          'Husband', 'Not-in-family', 'Wife', 'Own-child', 'Unmarried',
          'Other-relative'])

  workclass = tf.feature_column.categorical_column_with_vocabulary_list(
      'workclass', [
          'Self-emp-not-inc', 'Private', 'State-gov', 'Federal-gov',
          'Local-gov', '?', 'Self-emp-inc', 'Without-pay', 'Never-worked'])

  # To show an example of hashing:
  occupation = tf.feature_column.categorical_column_with_hash_bucket(
      'occupation', hash_bucket_size=1000)

  # Transformations.
  age_buckets = tf.feature_column.bucketized_column(
      age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])

  # Wide columns and deep columns.
  base_columns = [
      education, marital_status, relationship, workclass, occupation,
      age_buckets,
  ]

  crossed_columns = [
      tf.feature_column.crossed_column(
          ['education', 'occupation'], hash_bucket_size=1000),
      tf.feature_column.crossed_column(
          [age_buckets, 'education', 'occupation'], hash_bucket_size=1000),
  ]

  wide_columns = base_columns + crossed_columns

  deep_columns = [
      age,
      education_num,
      capital_gain,
      capital_loss,
      hours_per_week,
      tf.feature_column.indicator_column(workclass),
      tf.feature_column.indicator_column(education),
      tf.feature_column.indicator_column(marital_status),
      tf.feature_column.indicator_column(relationship),
      # To show an example of embedding
      tf.feature_column.embedding_column(occupation, dimension=8),
  ]

  return wide_columns, deep_columns


def build_estimator(model_dir, model_type):
  """Build an estimator appropriate for the given model type."""
  wide_columns, deep_columns = build_model_columns()
  hidden_units = [100, 75, 50, 25]

  # Create a tf.estimator.RunConfig to ensure the model is run on CPU, which
  # trains faster than GPU for this model.
  run_config = tf.estimator.RunConfig().replace(
      session_config=tf.ConfigProto(device_count={'GPU': 0}))

  if model_type == 'wide':
    return tf.estimator.LinearClassifier(
        model_dir=model_dir,
        feature_columns=wide_columns,
        config=run_config)
  elif model_type == 'deep':
    return tf.estimator.DNNClassifier(
        model_dir=model_dir,
        feature_columns=deep_columns,
        hidden_units=hidden_units,
        config=run_config)
  else:
    return tf.estimator.DNNLinearCombinedClassifier(
        model_dir=model_dir,
        linear_feature_columns=wide_columns,
        dnn_feature_columns=deep_columns,
        dnn_hidden_units=hidden_units,
        config=run_config)

class TfPhiReader: 
    def __init__(self):
        self.tf_aux_ii = 0
        self.nextrow = None

    def next(self, ii): 
        if self.tf_aux_ii == ii:
            if self.nextrow != None:
                sys.stderr.write("result set {0} read cached first row.\n".format(ii)) 
                ret = self.nextrow
                self.nextrow = None
                return ret[2:]
            else:
                rec = vitessedata.phi.NextInput()
                if rec == None:
                    sys.stderr.write("result set {0} read EOS".format(ii))
                    return None
                if rec[0] != ii:
                    sys.stderr.write("resultset switch from {0} to {1}\n".format(ii, rec[0]))
                    self.tf_aux_ii = rec[0]
                    self.nextrow = rec
                    return None
                else:
                    return rec[2:]
        else:
            sys.stderr.write("result set, try to read {0}, tf_aux_ii is {1}\n".format(ii, self.tf_aux_ii))
            if self.nextrow != None:
                sys.stderr.write("result set, try to read {0}, tf_aux_ii is {1}, cached mismatch\n".format(ii, self.tf_aux_ii))
                return None
            else:
                rec = vitessedata.phi.NextInput()
                if rec == None:
                    sys.stderr.write("result set {0}, tf_aux_ii {1} read EOS".format(ii, self.tf_aux_ii))
                    return None
                if rec[0] == ii:
                    self.tf_aux_ii = rec[0]
                    if rec[0] == ii:
                        return rec[2:]
                    else:
                        self.nextrow = rec
                        return None
            
tf_phi_reader = TfPhiReader()

def phi_generator(ii):
    cnt = 0
    sys.stderr.write("Begin reading resultset {0}\n".format(ii)) 
    rec = tf_phi_reader.next(ii)
    while rec != None:
        cnt += 1
        if cnt % 97 == 0:
            sys.stderr.write("Sample a Rec {0}: {1}.\n".format(cnt, str(rec)))
        yield tuple(rec)
        rec = tf_phi_reader.next(ii)
    sys.stderr.write("Done reading resultset {0}, total {1} records\n".format(ii, cnt)) 

def input_fn(ii): 
    ds = tf.data.Dataset.from_generator(lambda: phi_generator(ii), 
            (tf.float32, tf.string, tf.float32, tf.string, tf.float32,
             tf.string, tf.string, tf.string, tf.string, tf.string,
             tf.float32, tf.float32, tf.float32, tf.string, tf.string),
            ([], [], [], [], [],
             [], [], [], [], [],
             [], [], [], [], []))
    ds = ds.batch(FLAGS.batch_size)
    cols = ds.make_one_shot_iterator().get_next()
    features = dict(zip(_CSV_COLUMNS, cols))
    labels = features.pop('income_bracket')
    return features, tf.equal(labels, '>50K')

def main(unused_argv):
  # Clean up the model directory if present
  shutil.rmtree(FLAGS.model_dir, ignore_errors=True)
  model = build_estimator(FLAGS.model_dir, FLAGS.model_type)

  # Train and evaluate the model every `FLAGS.epochs_per_eval` epochs.
  for n in range(FLAGS.train_epochs // FLAGS.epochs_per_eval):
    model.train(input_fn=lambda: input_fn(0))
    results = model.evaluate(input_fn=lambda: input_fn(1))
    sys.stderr.write("Round {0}: accuracy is {1}.\n".format(n, results['accuracy'])) 
    vitessedata.phi.WriteOutput([n, float(results['accuracy'])])
  vitessedata.phi.WriteOutput(None)

if __name__ == '__main__':
    sys.stderr = open("/tmp/phi_py2.log", "w")
    tf.logging.set_verbosity(tf.logging.ERROR)
    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)

$PHI$), t.* from 
(select * from (
        select * from aaaa
        union all 
        select * from aaaa
        union all 
        select * from bbbb 
        union all 
        select * from aaaa
        union all 
        select * from aaaa
        union all 
        select * from bbbb 
    ) ut limit 1000000000000
) t
;
