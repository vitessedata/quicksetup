import dg.conn
import dg.xtable
import dg.tf.estimator

CONF_nround = 5 
if __name__ == '__main__':
    conn = dg.conn.Conn("ftian") 
    est = dg.tf.estimator.Estimator(batch_sz=40)
    est.add_out_col('falseneg', 'int')
    est.add_out_col('trueneg', 'int')
    est.add_out_col('falsepos', 'int')
    est.add_out_col('truepos', 'int')
    est.add_out_col('accuracy', 'float')

    xt1 = dg.xtable.fromTable(conn, 'widedeep_train')
    xt2 = dg.xtable.fromTable(conn, 'widedeep_test')

    for ii in range(CONF_nround): 
        est.tfinput.add_xt(xt1, repeat=2, shuffle=True)
        est.tfinput.add_xt(xt2)

    tfcode = """
import shutil

CONF_nround = 5
CONF_dir = '/tmp/census_model'
CONF_rmdir = True
CONF_model = 'wide_deep'   # can be wide, deep, wide_deep

def build_model_columns():
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

def input_fn(ii, cache_rs=False):
    features = sql_input_fn(ii, cache_rs)
    labels = features.pop('income')
    return features, tf.equal(labels, '>50K')

def array_input_fn(features):
    return features.pop('income'), None

def main(unused_args): 
    # Clean up the model directory if present
    if CONF_rmdir:
        shutil.rmtree(CONF_dir, ignore_errors=True)
    model = build_estimator(CONF_dir, CONF_model)

    for ii in range(CONF_nround): 
        model.train(input_fn=lambda: input_fn(ii*2))

        sql_clear_cached_rs()
        predict_res = model.predict(input_fn=lambda: input_fn(ii*2+1, cache_rs=True)) 
        predict_input = sql_cached_rs()
        falseneg, trueneg, falsepos, truepos = 0, 0, 0, 0

        idx = 0
        for predict in predict_res:
            data = predict_input[idx][-1]
            res = predict['class_ids'][0]
            idx += 1
            if data == '>50K':
                if res == 0:
                    falseneg += 1
                elif res == 1:
                    truepos += 1
                else:
                    raise ValueError("Bad result >50K?  [" + data + "] classified as " + str(res))
            elif data == '<=50K':
                if res == 0:
                    trueneg += 1
                elif res == 1:
                    falsepos += 1
                else:
                    raise ValueError("Bad result <=50K? [" + data + "] classified as " + str(res))
            else:
                raise ValueError("Bad result? [" + data + "] classified as " + str(res))

        vitessedata.phi.WriteOutput([falseneg, trueneg, falsepos, truepos, 
                        float(trueneg + truepos) / float(trueneg + truepos + falseneg + falsepos)]) 
    vitessedata.phi.WriteOutput(None)
"""

    est.add_tf_code(tfcode)

    estsql = est.build_sql()
    print(estsql)
    estxt = est.build_xt(conn)
    print(estxt.show())

