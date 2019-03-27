from sklearn import linear_model, svm, preprocessing
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
from joblib import dump
import csv


class MLModule(object):
	def loadData(self, csvFile):
		data = []
		lr_target = []
		svc_target = []
		with open(csvFile) as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			for row in reader:
				if (row[0] == "Switch"):
					svc_target.append(1)
				else:
					svc_target.append(0)
				
				lr_target.append(int(row[-1]))
				data.append([int(row[1])])
		print(data)
		return data, lr_target, svc_target
		
	def regression(self, data, target):
		##########################################
		# 1. Set model to linear regression model
		##########################################
		# Hint: use linear_model
		model = linear_model.LinearRegression()

		##########################################
		# 2. Split train and test datasets 70/30
		##########################################
		# Hint: use train_test_split.
		X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.3)

		##########################################
		# 3. Fit model to training data
		##########################################
		model.fit(X_train, y_train)

		##########################################
		# 4. Predict on test data
		##########################################
		y_pred = model.predict(X_test)

		##########################################
		# 5. Evaluate with MAE and MSE
		##########################################
		MAE = mean_absolute_error(y_test, y_pred)
		MSE = mean_squared_error(y_test, y_pred)
		print("Mean absolute error: " + str(MAE))
		print("Mean squared error: " + str(MSE))
		
		# Plot outputs
		plt.scatter(X_test, y_test,  color='black')
		plt.plot(X_test, y_pred, color='blue', linewidth=3)
		plt.xticks(())
		plt.yticks(())
		plt.show()

		dump(model, 'LR.joblib')

	def classification(self, data, target):
		model = None
		##########################################
		# 1. Set model to svm classifier
		##########################################
		model = make_pipeline(preprocessing.StandardScaler(), svm.SVC(C=1))

		##########################################
		# 2. Fit model to training data
		##########################################
		model.fit(data, target)

		##########################################
		# 3. Cross Validation
		##########################################
		# Hint: Use cross_val_score
		CVS = cross_val_score(model, data, target, cv=5)
		print("Cross validation score: " + str(CVS))
		
		dump(model, 'SVC.joblib')

ml = MLModule()
data, lr_target, svc_target = ml.loadData("mataData-2019_03_27_16_43_27.csv")
ml.classification(data, svc_target)
ml.regression(data, lr_target)
