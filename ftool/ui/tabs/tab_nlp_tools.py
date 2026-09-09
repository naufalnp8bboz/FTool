from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QSplitter, QProgressBar, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from ftool.config import THEME
from ftool.ui.components import FuturisticCard, NeonButton, StatCard
from ftool.core.nlp_engine import NLPEngine

SAMPLE_TEXT = """Artificial Intelligence and machine learning are revolutionizing software development.
With modern neural networks and automated workflows, complex engineering challenges become accessible to developers everywhere.
FTool provides an all-in-one suite designed to make machine learning, computer vision, and code transformation effortless, clean, and futuristic."""

class NLPToolsTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #1d2942; height: 4px; }")

        # Top Section: Text Analysis & Sentiment
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        # Stats Row
        stats_row = QHBoxLayout()
        self.stat_sentiment = StatCard("Sentiment Polarity", "Positive", color=THEME['accent_green'])
        self.stat_readability = StatCard("Reading Ease (Flesch)", "65.2", color=THEME['accent_cyan'])
        self.stat_words = StatCard("Word Count", "0", color=THEME['accent_purple'])
        self.stat_chars = StatCard("Character Count", "0", color=THEME['accent_cyan'])
        stats_row.addWidget(self.stat_sentiment)
        stats_row.addWidget(self.stat_readability)
        stats_row.addWidget(self.stat_words)
        stats_row.addWidget(self.stat_chars)
        top_layout.addLayout(stats_row)

        # Text Input Card
        text_card = FuturisticCard("NATURAL LANGUAGE ANALYSIS & SENTIMENT ENGINE")
        self.txt_input = QTextEdit()
        self.txt_input.setPlaceholderText("Type or paste any text to analyze sentiment, readability, and keywords...")
        self.txt_input.setPlainText(SAMPLE_TEXT)
        self.txt_input.textChanged.connect(self._analyze_text)
        text_card.addWidget(self.txt_input)

        # Keyword Chips Container
        self.lbl_keywords = QLabel("Top Keywords: -")
        self.lbl_keywords.setStyleSheet(f"font-size: 12px; color: {THEME['text_secondary']};")
        text_card.addWidget(self.lbl_keywords)

        top_layout.addWidget(text_card)
        splitter.addWidget(top_container)

        # Bottom Section: Cosine Text Similarity Comparator
        bottom_card = FuturisticCard("SEMANTIC SIMILARITY COMPARATOR (TF-IDF COSINE)")
        b_layout = QVBoxLayout()

        sim_boxes = QHBoxLayout()
        self.txt_sim1 = QTextEdit()
        self.txt_sim1.setPlaceholderText("Text Passage A...")
        self.txt_sim1.setPlainText("Machine learning models require clean training datasets and feature scaling.")
        self.txt_sim2 = QTextEdit()
        self.txt_sim2.setPlaceholderText("Text Passage B...")
        self.txt_sim2.setPlainText("Neural networks and data pipelines need scaled features and preprocessed data.")
        sim_boxes.addWidget(self.txt_sim1)
        sim_boxes.addWidget(self.txt_sim2)
        b_layout.addLayout(sim_boxes)

        sim_action = QHBoxLayout()
        btn_calc = NeonButton("⚡ CALCULATE COSINE SIMILARITY", variant="cyan")
        btn_calc.clicked.connect(self._calc_similarity)
        sim_action.addWidget(btn_calc)

        self.lbl_sim_score = QLabel("Similarity: 0.0%")
        self.lbl_sim_score.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {THEME['accent_cyan']}; margin-left: 10px;")
        sim_action.addWidget(self.lbl_sim_score)

        self.sim_progress = QProgressBar()
        self.sim_progress.setRange(0, 100)
        self.sim_progress.setValue(0)
        self.sim_progress.setFixedHeight(8)
        self.sim_progress.setTextVisible(False)
        sim_action.addWidget(self.sim_progress)

        b_layout.addLayout(sim_action)
        bottom_card.addLayout(b_layout)
        splitter.addWidget(bottom_card)

        main_layout.addWidget(splitter)

        # Initial calculation
        self._analyze_text()
        self._calc_similarity()

    def _analyze_text(self):
        text = self.txt_input.toPlainText()
        res = NLPEngine.analyze_text(text)

        self.stat_words.set_value(str(res["word_count"]))
        self.stat_chars.set_value(str(res["char_count"]))
        self.stat_readability.set_value(str(res["reading_ease"]))

        # Sentiment styling
        score = res["sentiment_score"]
        sent = res["sentiment"]
        self.stat_sentiment.set_value(f"{sent} ({score:+.2f})")

        # Keywords
        if res["top_keywords"]:
            chips = [f"#{k['word']} ({k['count']})" for k in res["top_keywords"]]
            self.lbl_keywords.setText("Top Keywords: " + "  •  ".join(chips))
        else:
            self.lbl_keywords.setText("Top Keywords: None")

    def _calc_similarity(self):
        t1 = self.txt_sim1.toPlainText()
        t2 = self.txt_sim2.toPlainText()
        sim = NLPEngine.calculate_similarity(t1, t2)
        self.lbl_sim_score.setText(f"Similarity: {sim:.1f}%")
        self.sim_progress.setValue(int(sim))
