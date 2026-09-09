import os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QSplitter, QScrollArea, QFrame, QLineEdit,
    QSlider, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton, StatCard, DarkPlotCanvas
from ftool.core.ml_engine import MLEngine

class MLStudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.ml_engine = MLEngine()
        self.single_predict_inputs = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top Control Bar (Dataset selection, Upload, Model select)
        top_bar = FuturisticCard()
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # Preset Dataset Selector
        top_layout.addWidget(QLabel("Dataset:"))
        self.combo_dataset = QComboBox()
        self.combo_dataset.addItems(["Iris (Classification)", "Customer Churn (Classification)", "Wine (Classification)", "Diabetes (Regression)"])
        self.combo_dataset.currentIndexChanged.connect(self._on_preset_selected)
        top_layout.addWidget(self.combo_dataset)

        btn_upload = NeonButton("Upload CSV / JSON", variant="cyan")
        btn_upload.clicked.connect(self._upload_file)
        top_layout.addWidget(btn_upload)

        top_layout.addSpacing(15)

        # Algorithm Selector
        top_layout.addWidget(QLabel("Algorithm:"))
        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["Random Forest", "Gradient Boosting", "Logistic Regression", "SVM", "KNN"])
        top_layout.addWidget(self.combo_algo)

        # Train Button
        self.btn_train = NeonButton("⚡ TRAIN MODEL", variant="purple")
        self.btn_train.clicked.connect(self._train_model)
        top_layout.addWidget(self.btn_train)

        # Code & Export Buttons
        btn_code = NeonButton("Python Code", variant="cyan")
        btn_code.clicked.connect(self._show_code_modal)
        top_layout.addWidget(btn_code)

        btn_export = NeonButton("Export .joblib", variant="green")
        btn_export.clicked.connect(self._export_model)
        top_layout.addWidget(btn_export)

        top_layout.addStretch()
        top_bar.addLayout(top_layout)
        main_layout.addWidget(top_bar)

        # Main Splitter: Left (Data & Config) | Right (Visualizations & Inference)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1d2942; width: 3px; }")

        # Left Panel (EDA & Table)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)

        # EDA Summary Cards
        eda_card = FuturisticCard("DATASET STATISTICAL OVERVIEW")
        eda_stats = QHBoxLayout()
        self.stat_rows = StatCard("Samples", "0", color=THEME['accent_cyan'])
        self.stat_cols = StatCard("Features", "0", color=THEME['accent_purple'])
        self.stat_target = StatCard("Target Column", "None", color=THEME['accent_green'])
        eda_stats.addWidget(self.stat_rows)
        eda_stats.addWidget(self.stat_cols)
        eda_stats.addWidget(self.stat_target)
        eda_card.addLayout(eda_stats)
        left_layout.addWidget(eda_card)

        # Table Preview
        table_card = FuturisticCard("DATA PREVIEW (FIRST 10 ROWS)")
        self.table_preview = QTableWidget()
        self.table_preview.setAlternatingRowColors(True)
        table_card.addWidget(self.table_preview)
        left_layout.addWidget(table_card)

        splitter.addWidget(left_widget)

        # Right Panel (Metrics, Visual Chart, Live Inference Sandbox)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(12)

        # Metrics Card
        metrics_card = FuturisticCard("TRAINING PERFORMANCE METRICS")
        m_layout = QHBoxLayout()
        self.stat_m1 = StatCard("Accuracy / R²", "-", color=THEME['accent_cyan'])
        self.stat_m2 = StatCard("F1 / MSE", "-", color=THEME['accent_purple'])
        self.stat_m3 = StatCard("Precision / MAE", "-", color=THEME['accent_green'])
        m_layout.addWidget(self.stat_m1)
        m_layout.addWidget(self.stat_m2)
        m_layout.addWidget(self.stat_m3)
        metrics_card.addLayout(m_layout)
        right_layout.addWidget(metrics_card)

        # Plot Card (Confusion Matrix or Feature Importances)
        plot_card = FuturisticCard("VISUAL EVALUATION & FEATURE IMPORTANCE")
        self.canvas = DarkPlotCanvas(width=5, height=3.5)
        plot_card.addWidget(self.canvas)
        right_layout.addWidget(plot_card)

        # Live Inference Sandbox
        self.sandbox_card = FuturisticCard("LIVE INFERENCE SANDBOX (TEST PREDICTION)")
        self.sandbox_layout = QVBoxLayout()
        self.sandbox_inputs_layout = QHBoxLayout()
        self.sandbox_layout.addLayout(self.sandbox_inputs_layout)
        
        infer_action_layout = QHBoxLayout()
        self.btn_predict = NeonButton("⚡ PREDICT OUTPUT", variant="cyan")
        self.btn_predict.clicked.connect(self._run_single_predict)
        self.lbl_predict_result = QLabel("Result: Ready for input")
        self.lbl_predict_result.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {THEME['accent_cyan']}; margin-left: 10px;")
        
        infer_action_layout.addWidget(self.btn_predict)
        infer_action_layout.addWidget(self.lbl_predict_result)
        infer_action_layout.addStretch()
        self.sandbox_layout.addLayout(infer_action_layout)
        
        self.sandbox_card.addLayout(self.sandbox_layout)
        right_layout.addWidget(self.sandbox_card)

        right_scroll.setWidget(right_widget)
        splitter.addWidget(right_scroll)

        main_layout.addWidget(splitter)

        # Load initial default dataset
        self._load_dataset_preset("iris")

    def _on_preset_selected(self, index: int):
        mapping = {
            0: "iris",
            1: "customer_churn",
            2: "wine",
            3: "diabetes"
        }
        name = mapping.get(index, "iris")
        self._load_dataset_preset(name)

    def _load_dataset_preset(self, name: str):
        try:
            df = self.ml_engine.load_sample_dataset(name)
            self._update_eda_display()
            # Update algorithm options depending on task type
            self.combo_algo.clear()
            if self.ml_engine.task_type == "classification":
                self.combo_algo.addItems(["Random Forest", "Gradient Boosting", "Logistic Regression", "SVM", "KNN"])
            else:
                self.combo_algo.addItems(["Random Forest", "Linear Regression", "Gradient Boosting", "SVR"])
            # Auto train on load for instant beginner gratification
            self._train_model()
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Dataset", str(e))

    def _upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Dataset", "", "Data Files (*.csv *.json *.xlsx *.xls)"
        )
        if file_path:
            try:
                self.ml_engine.load_file(file_path)
                # Ask user for target column
                cols = list(self.ml_engine.df.columns)
                target_col = cols[-1] # Default to last column
                self.ml_engine.target_name = target_col
                
                # Check if target is numeric with many unique values -> regression, else classification
                is_num = np.issubdtype(self.ml_engine.df[target_col].dtype, np.number)
                unique_cnt = self.ml_engine.df[target_col].nunique()
                if is_num and unique_cnt > 15:
                    self.ml_engine.task_type = "regression"
                else:
                    self.ml_engine.task_type = "classification"

                self._update_eda_display()
                self._train_model()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _update_eda_display(self):
        eda = self.ml_engine.get_auto_eda()
        if not eda:
            return

        self.stat_rows.set_value(str(eda["rows"]))
        self.stat_cols.set_value(str(eda["columns"]))
        self.stat_target.set_value(self.ml_engine.target_name)

        # Update Table Preview
        df = self.ml_engine.df
        self.table_preview.clear()
        self.table_preview.setRowCount(min(10, len(df)))
        self.table_preview.setColumnCount(len(df.columns))
        self.table_preview.setHorizontalHeaderLabels(list(df.columns))

        for r in range(min(10, len(df))):
            for c, col in enumerate(df.columns):
                val = str(df.iloc[r, c])
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_preview.setItem(r, c, item)

    def _train_model(self):
        if self.ml_engine.df is None:
            return
        algo = self.combo_algo.currentText()
        try:
            metrics = self.ml_engine.train(
                target_col=self.ml_engine.target_name,
                model_name=algo,
                task_type=self.ml_engine.task_type
            )

            # Update Metric Cards
            if metrics["task"] == "classification":
                self.stat_m1.set_value(f"{metrics['accuracy'] * 100:.1f}%")
                self.stat_m2.set_value(f"{metrics['f1_score']:.3f}")
                self.stat_m3.set_value(f"{metrics['precision']:.3f}")
            else:
                self.stat_m1.set_value(f"{metrics['r2_score']:.3f}")
                self.stat_m2.set_value(f"{metrics['mse']:.3f}")
                self.stat_m3.set_value(f"{metrics['mae']:.3f}")

            # Plot visual evaluation
            self._render_plot(metrics)

            # Build inference inputs
            self._build_inference_inputs()

        except Exception as e:
            QMessageBox.warning(self, "Training Error", str(e))

    def _render_plot(self, metrics):
        self.canvas.fig.clf()
        ax = self.canvas.fig.add_subplot(111)
        ax.set_facecolor(THEME['bg_card'])

        if metrics["task"] == "classification" and "confusion_matrix" in metrics:
            cm = np.array(metrics["confusion_matrix"])
            classes = metrics.get("classes", [str(i) for i in range(len(cm))])
            
            cax = ax.matshow(cm, cmap="Blues", alpha=0.85)
            self.canvas.fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)

            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > cm.max()/2 else "#00e5ff", fontweight="bold", fontsize=11)

            ax.set_xticks(range(len(classes)))
            ax.set_yticks(range(len(classes)))
            ax.set_xticklabels(classes, color=THEME['text_secondary'], fontsize=9)
            ax.set_yticklabels(classes, color=THEME['text_secondary'], fontsize=9)
            ax.set_title("Confusion Matrix Heatmap", color="white", fontsize=11, pad=12, fontweight="bold")
            ax.set_xlabel("Predicted Label", color=THEME['text_secondary'], fontsize=10)
            ax.set_ylabel("True Label", color=THEME['text_secondary'], fontsize=10)

        elif "feature_importances" in metrics and metrics["feature_importances"]:
            fi = metrics["feature_importances"]
            features = list(fi.keys())[:8]
            scores = [fi[f] for f in features]
            
            y_pos = np.arange(len(features))
            bars = ax.barh(y_pos, scores, align='center', color="#00e5ff", edgecolor="#7c4dff")
            ax.set_yticks(y_pos)
            ax.set_yticklabels(features, color=THEME['text_secondary'], fontsize=9)
            ax.invert_yaxis()
            ax.set_xlabel("Importance Score", color=THEME['text_secondary'], fontsize=10)
            ax.set_title("Feature Importances", color="white", fontsize=11, fontweight="bold")
            ax.tick_params(colors=THEME['text_secondary'])
        else:
            ax.text(0.5, 0.5, "Model Evaluation Complete", ha="center", va="center", color=THEME['accent_cyan'], fontsize=14)

        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def _build_inference_inputs(self):
        # Clear existing
        while self.sandbox_inputs_layout.count():
            item = self.sandbox_inputs_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.single_predict_inputs = {}
        df = self.ml_engine.df

        # Max 5 feature inputs in sandbox row
        features = self.ml_engine.feature_names[:5]
        for f in features:
            box = QVBoxLayout()
            lbl = QLabel(f[:15])
            lbl.setStyleSheet(f"font-size: 11px; color: {THEME['text_secondary']};")
            
            # Use mean value as default
            mean_val = "0.0"
            if f in df and np.issubdtype(df[f].dtype, np.number):
                mean_val = f"{df[f].mean():.2f}"

            inp = QLineEdit(mean_val)
            inp.setFixedWidth(90)
            box.addWidget(lbl)
            box.addWidget(inp)
            self.sandbox_inputs_layout.addLayout(box)
            self.single_predict_inputs[f] = inp

    def _run_single_predict(self):
        try:
            inputs = {}
            for f, inp in self.single_predict_inputs.items():
                val_text = inp.text().strip()
                try:
                    inputs[f] = float(val_text)
                except ValueError:
                    inputs[f] = val_text

            res = self.ml_engine.predict_single(inputs)
            pred = res.get("prediction", "Unknown")
            
            probs_str = ""
            if "probabilities" in res:
                top_prob = max(res["probabilities"].items(), key=lambda x: x[1])
                probs_str = f" (Confidence: {top_prob[1]*100:.1f}%)"

            self.lbl_predict_result.setText(f"PREDICTION: {pred}{probs_str}")
        except Exception as e:
            self.lbl_predict_result.setText(f"Error: {e}")

    def _show_code_modal(self):
        code = self.ml_engine.generate_python_code()
        dialog = QDialog(self)
        dialog.setWindowTitle("Generated Python Training & Inference Code")
        dialog.resize(650, 500)
        d_layout = QVBoxLayout(dialog)

        txt = QTextEdit()
        txt.setPlainText(code)
        txt.setReadOnly(True)
        txt.setFontFamily("Consolas")
        d_layout.addWidget(txt)

        btn_copy = NeonButton("Copy Code to Clipboard", variant="cyan")
        btn_copy.clicked.connect(lambda: (txt.selectAll(), txt.copy(), QMessageBox.information(dialog, "Copied", "Python code copied to clipboard!")))
        d_layout.addWidget(btn_copy)

        dialog.exec()

    def _export_model(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Trained Model", "trained_model.joblib", "Joblib Files (*.joblib)")
        if file_path:
            try:
                self.ml_engine.export_model(file_path)
                QMessageBox.information(self, "Export Successful", f"Model pipeline saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
