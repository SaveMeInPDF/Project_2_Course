# Установка и загрузка библиотек
if (!require("xgboost")) install.packages("xgboost", dependencies = TRUE)
if (!require("caret")) install.packages("caret", dependencies = TRUE)
if (!require("data.table")) install.packages("data.table", dependencies = TRUE)
if (!require("dplyr")) install.packages("dplyr", dependencies = TRUE)

library(xgboost)
library(caret)
library(data.table)
library(dplyr)

# Загрузка данных
data <- fread("correlated_network_data.csv")

# Заменим все пробелы и символы / на подчеркивания в именах столбцов
colnames(data) <- gsub(" ", "_", colnames(data))  # Заменяем пробелы на подчеркивания
colnames(data) <- gsub("/", "_", colnames(data))  # Заменяем символы / на подчеркивания

# Создание новой целевой переменной на основе порога Anomaly_Scores и значения "None" в Attack_Type
data[, Anomaly := ifelse(Anomaly_Scores > 0.5, 1, 0)]

# Удалим старый столбец Anomaly_Scores
features <- data[, !c("Anomaly_Scores", "Anomaly", "Attack_Type"), with = FALSE]

# Преобразуем категориальные признаки в one-hot encoding
dummies <- dummyVars(Anomaly ~ ., data = data)
features_matrix <- predict(dummies, newdata = data)

# Целевая переменная
target <- data$Anomaly

# Деление на train/test
set.seed(42)
train_index <- createDataPartition(target, p = 0.6, list = FALSE)
train_data <- features_matrix[train_index, ]
test_data <- features_matrix[-train_index, ]
train_label <- target[train_index]
test_label <- target[-train_index]

# Преобразуем в DMatrix
dtrain <- xgb.DMatrix(data = train_data, label = train_label)
dtest <- xgb.DMatrix(data = test_data, label = test_label)

# Параметры модели
params <- list(
  objective = "binary:logistic",
  eval_metric = "logloss",
  eta = 0.01,               # Скорость обучения
  max_depth = 6,            # Глубина деревьев
  min_child_weight = 3,     # Минимум примеров в листьях
  subsample = 0.5,          # Bыборкa для тренировки
  colsample_bytree = 0.5,   # Признаки для дерева
  lambda = 1,               # L2 регуляризация
  alpha = 0.1               # L1 регуляризация
)

# Обучение модели
model <- xgb.train(
  params = params,
  data = dtrain,
  nrounds = 100,   # Количество итераций
  watchlist = list(train = dtrain, test = dtest),
  verbose = 1
)

# Предсказания
pred_probs <- predict(model, dtest)

# Применение порога 0.8
preds <- ifelse(pred_probs > 0.8, 1, 0)

# Точность
accuracy <- sum(preds == test_label) / length(test_label)
cat("Accuracy на тестовой выборке (Anomaly):", round(accuracy * 100, 2), "%\n")

