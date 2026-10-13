from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, train_test_split


RANDOM_STATE = 42
DATA_FILE = Path(__file__).with_name("pore.xlsx")
RESULTS_DIR = Path(__file__).with_name("xgboost-results")


def configure_plot_style():
    plt.rcParams["font.sans-serif"] = [
        "SimHei",
        "Microsoft YaHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def calculate_metrics(y_true, y_pred):
    return {
        "R2": float(r2_score(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
    }


def make_param_grid():
    return {
        "max_depth": range(4, 12, 1),
        "n_estimators": range(20, 220, 20),
        "gamma": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        "learning_rate": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
    }


def make_estimator(params=None):
    base_params = {
        "random_state": RANDOM_STATE,
        "n_jobs": 1,
    }
    if params:
        base_params.update(params)
    return xgb.XGBRegressor(**base_params)


def find_best_params(X_train, y_train):
    param_test1 = make_param_grid()
    grid_search = GridSearchCV(
        estimator=xgb.XGBRegressor(),
        param_grid=param_test1,
        scoring="r2",
        n_jobs=-1,
        verbose=1,
    )
    grid_search.fit(X_train, y_train)
    return grid_search.best_params_, float(grid_search.best_score_)


def save_fit_plot(
    output_path,
    title,
    y_train,
    train_prediction,
    y_test,
    test_prediction,
    metrics,
):
    figure, axis = plt.subplots(figsize=(5.2, 5.0))
    axis.scatter(
        y_train,
        train_prediction,
        marker="s",
        facecolors="none",
        edgecolors="#168AAD",
        linewidths=1.0,
        s=24,
        label="Training",
    )
    axis.scatter(
        y_test,
        test_prediction,
        marker="s",
        facecolors="none",
        edgecolors="#E63946",
        linewidths=1.0,
        s=28,
        label="Testing",
    )
    values = np.concatenate(
        [
            np.asarray(y_train),
            np.asarray(train_prediction),
            np.asarray(y_test),
            np.asarray(test_prediction),
        ]
    )
    lower = float(values.min())
    upper = float(values.max())
    margin = (upper - lower) * 0.05 if upper > lower else 1.0
    axis.plot(
        [lower - margin, upper + margin],
        [lower - margin, upper + margin],
        color="black",
        linewidth=1.0,
    )
    axis.set_xlim(lower - margin, upper + margin)
    axis.set_ylim(lower - margin, upper + margin)
    axis.set_xlabel("Test values", fontweight="bold")
    axis.set_ylabel("Prediction values", fontweight="bold")
    axis.text(
        0.97,
        0.04,
        f"R2={metrics['R2']:.4f}\n"
        f"RMSE={metrics['RMSE']:.4f}\n"
        f"MAE={metrics['MAE']:.4f}",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontweight="bold",
        fontsize=9,
    )
    handles, labels = axis.get_legend_handles_labels()
    labels = [
        f"Testing" if label == "Testing" else label
        for label in labels
    ]
    axis.legend(handles, labels, loc="upper left", frameon=False, fontsize=9)
    figure.tight_layout()
    figure.savefig(output_path, dpi=600, bbox_inches="tight")
    plt.close(figure)


def five_fold_validation(X_data, y_data, target_name, model_params, output_dir):
    kfold = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    fold_metrics = []

    for fold, (train_index, validation_index) in enumerate(
        kfold.split(X_data), start=1
    ):
        X_fold_train = X_data.iloc[train_index]
        X_fold_validation = X_data.iloc[validation_index]
        y_fold_train = y_data.iloc[train_index]
        y_fold_validation = y_data.iloc[validation_index]

        model = make_estimator(model_params)
        model.fit(X_fold_train, y_fold_train)
        train_prediction = model.predict(X_fold_train)
        validation_prediction = model.predict(X_fold_validation)
        metrics = calculate_metrics(y_fold_validation, validation_prediction)
        fold_metrics.append(metrics)

        save_fit_plot(
            output_dir / f"五折交叉验证_第{fold}折.png",
            f"{target_name} - 第 {fold} 折",
            y_fold_train,
            train_prediction,
            y_fold_validation,
            validation_prediction,
            metrics,
        )

    metrics_frame = pd.DataFrame(
        fold_metrics, index=[f"第{i}折" for i in range(1, 6)]
    )
    with (output_dir / "五折交叉验证指标.txt").open("w", encoding="utf-8") as file:
        file.write(f"{target_name} 五折交叉验证指标\n")
        file.write("=" * 56 + "\n")
        for fold_name, row in metrics_frame.iterrows():
            file.write(
                f"{fold_name}: R2={row['R2']:.6f}, "
                f"RMSE={row['RMSE']:.6f}, MAE={row['MAE']:.6f}\n"
            )


def save_final_outputs(
    model, X_train, X_test, y_train, y_test, target_name, output_dir, params, best_score
):
    train_prediction = model.predict(X_train)
    test_prediction = model.predict(X_test)
    train_metrics = calculate_metrics(y_train, train_prediction)
    test_metrics = calculate_metrics(y_test, test_prediction)

    save_fit_plot(
        output_dir / "最终训练集和测试集拟合图.png",
        "",
        y_train,
        train_prediction,
        y_test,
        test_prediction,
        test_metrics,
    )

    with (output_dir / "最终模型指标和超参数.txt").open(
        "w", encoding="utf-8"
    ) as file:
        file.write(f"{target_name} 最终模型结果\n")
        file.write("=" * 56 + "\n")
        file.write("训练集指标:\n")
        for key in ("R2", "RMSE", "MAE"):
            file.write(f"{key}: {train_metrics[key]:.6f}\n")
        file.write("\n测试集指标:\n")
        for key in ("R2", "RMSE", "MAE"):
            file.write(f"{key}: {test_metrics[key]:.6f}\n")
        file.write("\n网格搜索最佳超参数:\n")
        file.write(f"best_cv_R2: {best_score:.6f}\n")
        for key, value in params.items():
            file.write(f"{key}: {value}\n")

# 保存图片的同时将结果也保存一份到excel，总的shap图和各个输入变量的依赖图
def save_shap_outputs(model, X_train, X_test, output_dir):
    explainer = shap.TreeExplainer(model)
    shap_values = np.asarray(explainer.shap_values(X_test))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.savefig(output_dir / "SHAP_summary.png", dpi=600, bbox_inches="tight")
    plt.close()

    summary_feature_values = X_test.reset_index(drop=True).add_prefix("feature_value_")
    summary_shap_values = pd.DataFrame(
        shap_values,
        columns=[f"shap_value_{feature_name}" for feature_name in X_test.columns],
    )
    pd.concat([summary_feature_values, summary_shap_values], axis=1).to_excel(
        output_dir / "SHAP_summary.xlsx", index=False
    )

    shap_values_all = np.asarray(explainer.shap_values(X_train))
    for feature_name in X_test.columns:
        shap.dependence_plot(
            feature_name,
            shap_values_all,
            X_train,
            display_features=X_train,
            show=False,
        )
        safe_name = str(feature_name).replace("/", "_")
        plt.savefig(
            output_dir / f"SHAP_dependence_{safe_name}.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        feature_index = X_train.columns.get_loc(feature_name)
        dependence_data = X_train.reset_index(drop=True).copy()
        dependence_data.insert(
            0,
            f"shap_value_{feature_name}",
            shap_values_all[:, feature_index],
        )
        dependence_data.insert(
            0,
            f"feature_value_{feature_name}",
            X_train[feature_name].to_numpy(),
        )
        dependence_data.to_excel(
            output_dir / f"SHAP_dependence_{safe_name}.xlsx", index=False
        )


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"未找到数据文件: {DATA_FILE}")

    data = pd.read_excel(DATA_FILE)
    if data.shape[1] < 8:
        raise ValueError("pore.xlsx 至少需要包含 5 个特征列和 3 个目标列。")

    features = data.iloc[:, :5].copy()
    features.columns = ["dG", "H", "O", "Layer", "Pore"]
    targets = data.iloc[:, 5:8].copy()
    targets.columns = ["pass-wa", "Na_rejection", "Cl_rejection"]
    features = features.apply(pd.to_numeric, errors="coerce")
    targets = targets.apply(pd.to_numeric, errors="coerce")
    valid = features.notna().all(axis=1) & targets.notna().all(axis=1)
    return (
        features.loc[valid].reset_index(drop=True),
        targets.loc[valid].reset_index(drop=True),
    )


def train_one_target(X, y, target_name, folder_name):
    output_dir = RESULTS_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    best_params, best_score = find_best_params(X_train, y_train)
    five_fold_validation(X_train, y_train, target_name, best_params, output_dir)
    model = make_estimator(best_params)
    model.fit(X_train, y_train)
    save_final_outputs(
        model, X_train, X_test, y_train, y_test, target_name, output_dir, best_params, best_score
    )
    save_shap_outputs(model, X_train, X_test, output_dir)


def main():
    configure_plot_style()
    X, targets = load_data()
    target_settings = [
        ("pass-wa", "水通量"),
        ("Na_rejection", "Na"),
        ("Cl_rejection", "Cl"),
    ]

    for target_name, folder_name in target_settings:
        train_one_target(X, targets[target_name], target_name, folder_name)

    print(f"结果已保存到: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
