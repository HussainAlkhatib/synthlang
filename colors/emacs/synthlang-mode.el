;; SynthLang major mode for Emacs
(defvar synthlang-keywords
  '("let" "var" "fn" "if" "elif" "else" "for" "while" "return" 
    "go" "await" "match" "defer" "try" "handle" "panic" "in" "as" "module")
  "SynthLang keywords.")

(defvar synthlang-types
  '("int" "float" "str" "string" "bool" "void" "list" "dict" "object")
  "SynthLang types.")

(defvar synthlang-font-lock-keywords
  `((,(regexp-opt synthlang-keywords 'words) . font-lock-keyword-face)
    (,(regexp-opt synthlang-types 'words) . font-lock-type-face)
    ("\\(true\\|false\\)" . font-lock-constant-face)
    ("@[a-zA-Z_][a-zA-Z0-9_]*" . font-lock-preprocessor-face)
    ("@\\(python\\|javascript\\|rust\\|c\\|go\\|java\\)\\s-+module\\s-+\"[^\"]*\"\\s-+\\(as\\|import\\)\\s-+[a-zA-Z_][a-zA-Z0-9_, ]*" . font-lock-include-face)
    ("#.*$" . font-lock-comment-face)
    ("//.*$" . font-lock-comment-face)
    ("/\\*.*?\\*/" . font-lock-comment-face)
    ("\"[^\"]*\"" . font-lock-string-face)
    ("'[^']*'" . font-lock-string-face)
    ("\\(\\+\\|-\\|\\*\\|/\\|%\\|==\\|!=\\|<=\\|>=\\|<\\|>\\|&&\\|||\\|!\\)" . font-lock-operator-face)
    ("\\b[0-9]+\\b" . font-lock-constant-face)
    ("\\b[0-9]+\\.[0-9]+\\b" . font-lock-constant-face))
  "SynthLang font lock keywords.")

(define-derived-mode synthlang-mode prog-mode "SynthLang"
  "Major mode for editing SynthLang files."
  (setq font-lock-defaults '((synthlang-font-lock-keywords)))

(add-to-list 'auto-mode-alist '("\\.sl\\'" . synthlang-mode))

(provide 'synthlang-mode)