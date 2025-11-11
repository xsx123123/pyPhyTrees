# pyPhyTrees

使用 MAFFT 和 IQ-TREE 进行系统发育树构建和可视化的 Python 脚本。

## 概述

该脚本通过以下方式自动化系统发育树构建过程：
- 使用 MAFFT 对序列进行比对
- 使用 IQ-TREE 构建系统发育树
- 创建各种可视化，包括圆形、矩形、径向和热图布局

### 新功能
- **自定义颜色支持**：使用 CSV 文件通过 `--relation` 参数为组指定自定义颜色
- **多种可视化样式**：支持圆形、矩形、径向和热图可视化
- **基于距离的着色**：默认基于进化距离着色（可以用分组覆盖）
- **基于 CSV 的分组**：支持通过 CSV 文件指定序列组，格式为：`sequence,group,color`（颜色可选）

## 依赖项

### 必需软件

脚本需要以下外部工具安装并可在 PATH 中使用：

1. **MAFFT** v7.525 或更高版本
   - 测试版本：v7.526 (2024/Apr/26)
   - 多序列比对工具
   - 主页：https://mafft.cbrc.jp/alignment/software/

2. **IQ-TREE** v3.0.1 或更高版本
   - 测试版本：v3.0.1 (2025/May/5)
   - 系统发育树推断软件
   - 主页：http://www.iqtree.org

### Python 依赖项

脚本需要以下 Python 包：

- Biopython
- pycirclize
- matplotlib
- pandas
- rich
- hydra-core
- omegaconf

## 安装

### 安装外部依赖

#### 使用 Conda
```bash
conda install -c bioconda mafft iqtree
```

#### 手动安装
- 从以下地址下载 MAFFT：https://mafft.cbrc.jp/alignment/software/
- 从以下地址下载 IQ-TREE：http://www.iqtree.org

### 安装 Python 依赖项

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法
```bash
python main.py sequences.fasta
```

### 自定义输出和参数
```bash
python main.py sequences.fasta -o my_tree.png --seq-type dna -B 1000
```

### 使用传统格式进行分组可视化
```bash
python main.py sequences.fasta -g 'Group1:seq1,seq2' -g 'Group2:seq3,seq4'
```

### 使用 CSV 文件进行分组可视化（新功能）
创建格式为：`sequence,group,color` 的 CSV 文件（颜色可选）
```csv
sequence,group,color
seq1,GroupA,#FF0000
seq2,GroupA,#FF0000
seq3,GroupB,#0000FF
seq4,GroupB,#0000FF
```

然后使用：
```bash
python main.py sequences.fasta --relation groups.csv
```

### 多种可视化样式
```bash
# 圆形可视化（默认）
python main.py sequences.fasta --visualization-style circular

# 矩形可视化
python main.py sequences.fasta --visualization-style rectangular

# 径向可视化
python main.py sequences.fasta --visualization-style radial

# 热图可视化
python main.py sequences.fasta --visualization-style heatmap

# 所有样式
python main.py sequences.fasta --visualization-style all
```

### 详细帮助
```bash
python main.py --help-rich
```

### 显示徽标
```bash
python main.py --show-logo
```

## 命令行选项

### 构建命令（用于从序列创建树）
| 选项 | 说明 | 默认值 |
|--------|-------------|---------|
| `INPUT_FILE` | 包含序列的输入 FASTA 文件 | |
| `-o, --output` | 输出图像文件名 | `phylogenetic_tree_circular.png` |
| `--tree-file` | 以 Newick 格式输出的树文件 | `tree.nwk` |
| `--alignment-file` | 以 FASTA 格式输出的比对文件 | `aligned.fasta` |
| `--seq-type` | 序列类型（如未提供则自动检测） | `auto` |
| `-B, --bootstrap` | IQ-TREE 的 Ultrafast Bootstrap 重复次数（最少 1000） | `100`（将调整为最少 1000） |
| `--threads` | MAFFT 和 IQ-TREE 使用的线程数 | `1` |
| `-g, --group` | 用于可视化的分组物种（格式：GroupName:Species1,Species2,...）。可多次使用。 | |
| `--relation` | 包含序列到组关系的 CSV 文件（格式：'sequence,group' 列） | |
| `--visualization-style` | 要生成的可视化类型（圆形、矩形、径向、热图、全部） | `circular` |
| `--keep-all-files` | 保留所有中间文件（比对、日志等） | `False` |

### 绘图命令（用于可视化现有树）
| 选项 | 说明 | 默认值 |
|--------|-------------|---------|
| `TREE_FILE` | 输入 Newick 格式的树文件 | |
| `-o, --output` | 输出图像文件名 | `phylogenetic_tree_circular.png` |
| `-g, --group` | 用于可视化的分组物种（格式：GroupName:Species1,Species2,...）。可多次使用。 | |
| `--relation` | 包含序列到组关系的 CSV 文件（格式：'sequence,group' 列） | |
| `--visualization-style` | 要生成的可视化类型（圆形、矩形、径向、热图、全部） | `circular` |

## 组关系的 CSV 格式

`--relation` 选项接受包含以下列的 CSV 文件：
- `sequence`：FASTA/系统发育树中出现的序列名称
- `group`：此序列的组名
- `color`（可选）：此组的十六进制颜色代码（例如 #FF0000，红色）

示例 CSV 文件：
```csv
sequence,group,color
gene00975,GroupA,#FF0000
gene01152,GroupA,#FF0000
gene03450,GroupA,#FF0000
gene01844,GroupB,#0000FF
gene04400,GroupB,#0000FF
gene01985,GroupC,#00FF00
gene08479,GroupC,#00FF00
```

您也可以使用不带颜色的简单格式，系统将自动分配颜色：
```csv
sequence,group
seq1,GroupA
seq2,GroupA
seq3,GroupB
seq4,GroupB
```

## 功能

- **自动序列类型检测**：自动检测序列是 DNA、RNA 还是蛋白质
- **丰富的格式化输出**：具有徽标和帮助的精美命令行界面
- **多种可视化样式**：创建各种格式的出版物级可视化
- **分组可视化**：使用自定义颜色对可视化中的不同物种组进行着色
- **基于距离的着色**：默认基于进化距离着色
- **自动文件清理**：完成后的中间文件（除非指定 `--keep-all-files`）
- **灵活分组**：支持传统的 `-g` 标志和基于 CSV 的分组
- **图例支持**：所有可视化都包含显示组-颜色映射的图例

## 输入要求

- 构建树时输入文件必须是 FASTA 格式
- 绘制现有树时，使用 Newick 格式 (.nwk)
- 系统发育分析至少需要 3 个序列
- 用于分组的 CSV 文件必须包含 'sequence' 和 'group' 列

## 输出

- 系统发育树的各种可视化（取决于所选样式）
- Newick 树文件（默认：`tree.nwk`）
- 可选的比对文件和 IQ-TREE 输出文件
- 使用分组时，所有可视化都包含图例

## 故障排除

### 常见问题

1. **命令未找到**：
   - 确保已安装 MAFFT 和 IQ-TREE 并在 PATH 中
   - 使用 `mafft -v` 和 `iqtree3 -v` 验证安装

2. **IQ-TREE bootstrap 要求**：
   - 脚本会自动将 bootstrap 值调整为 IQ-TREE 所需的最低 1000

3. **可视化库缺失**：
   - 使用以下命令安装：`pip install -r requirements.txt`

4. **CSV 文件格式错误**：
   - 确保 CSV 文件中存在必需的 'sequence' 和 'group' 列
   - 检查序列名称是否与 FASTA/系统发育树中的匹配

5. **颜色格式错误**：
   - 使用自定义颜色时，确保为有效的十六进制格式（例如 #FF0000）

## 示例

### 基本树构建和可视化
```bash
python main.py sequences.fasta -o my_tree.png
```

### 使用自定义组构建
```bash
python main.py sequences.fasta --relation groups.csv --visualization-style all
```

### 使用自定义组可视化现有树
```bash
python main.py plot tree.nwk --relation groups.csv --visualization-style rectangular
```

## 许可证

此项目是开源的。有关详细信息，请参阅 LICENSE 文件。