# MooTDX API 完整参考文档

> **文档来源**: https://github.com/mootdx/mootdx/tree/master/docs/api
> **整理日期**: 2025-09-30
> **用途**: SimTradeData 项目 mootdx 数据源集成参考

---

## 目录

1. [财务数据 (Affair)](#财务数据-affair)
2. [标准行情 (Quotes)](#标准行情-quotes)
3. [本地数据读取 (Reader)](#本地数据读取-reader)
4. [扩展功能 (Extras)](#扩展功能-extras)
5. [字段对照表](#字段对照表)

---

## 财务数据 (Affair)

### 核心概念

- mootdx 的财务数据存储在 ZIP 文件中
- 每个文件包含一个报告期的所有股票财务数据
- 文件命名格式: `gpcw{YYYYMMDD}.zip`，如 `gpcw20230630.zip` (2023年中报)
- 支持 322 个 FINVALUE 财务字段

### 1. 获取财务数据文件列表

```python
from mootdx.affair import Affair

# 获取所有可用的财务数据文件
files = Affair.files()

# 返回格式:
# [
#   {'filename': 'gpcw20230630.zip', 'hash': '...', 'filesize': 5544177},
#   {'filename': 'gpcw20230331.zip', 'hash': '...', 'filesize': 5234567},
#   ...
# ]
```

**返回字段说明**:
- `filename`: 文件名
- `hash`: MD5 哈希值（用于检查是否需要更新）
- `filesize`: 文件大小（字节）

### 2. 下载财务数据文件

```python
from mootdx.affair import Affair

# 下载指定报告期的财务数据
Affair.fetch(downdir='data/financial', filename='gpcw20230630.zip')
```

**参数说明**:
- `downdir`: 下载目录
- `filename`: 要下载的文件名（从 `Affair.files()` 获取）

### 3. 解析财务数据

```python
from mootdx.affair import Affair

# 解析已下载的财务数据文件
data = Affair.parse(downdir='data/financial', filename='gpcw20230630.zip')

# 也支持解析 .dat 文件（解压后的文件）
data = Affair.parse(downdir='data/financial', filename='gpcw20230630.dat')

# 返回 pandas.DataFrame，包含所有股票的财务数据
```

**返回数据格式**:
- DataFrame，每行代表一只股票
- 列名为 FINVALUE 字段编号或中文字段名
- 具体字段参见 [字段对照表](#字段对照表)

### 4. 保存财务数据

```python
from mootdx.affair import Affair

result = Affair.parse(downdir='data/financial', filename='gpcw20230630.zip')

# 保存为 CSV
result.to_csv('financial_20230630.csv', index=False)

# 保存为 Excel
result.to_excel('financial_20230630.xlsx', index=False)
```

---

## 标准行情 (Quotes)

### 初始化

```python
from mootdx.quotes import Quotes

# 标准市场（沪深股票）
client = Quotes.factory(market='std')

# 扩展市场（其他市场）
client = Quotes.factory(market='ext')

# 高级参数
client = Quotes.factory(
    market='std',
    multithread=True,   # 多线程
    heartbeat=True,     # 心跳包
    bestip=False,       # 自动选择最快服务器
    timeout=15,         # 超时时间
    quiet=False,        # 日志静默
    verbose=1           # 日志级别 (0-2)
)
```

### 1. 实时行情

```python
# 获取单个或多个股票实时行情
df = client.quotes(symbols=["000001", "600036"])

# 返回字段：
# - code: 股票代码
# - price: 当前价
# - last_close: 昨收
# - open: 今开
# - high: 最高
# - low: 最低
# - vol: 成交量
# - amount: 成交额
# - bid/ask: 买卖盘口
```

### 2. K线数据

```python
# 日K线
df = client.bars(symbol='600036', frequency=9, start=0, offset=800)

# 分钟K线
df = client.bars(symbol='600036', frequency=0, start=0, offset=240)  # 5分钟

# frequency 参数:
# 0 => 5分钟
# 1 => 15分钟
# 2 => 30分钟
# 3 => 1小时
# 4/9 => 日K线
# 5 => 周K线
# 6 => 月K线
# 7/8 => 1分钟
# 10 => 季K线
# 11 => 年K线

# 前复权
df = client.bars(symbol='600036', frequency=9, adjust='qfq')

# 后复权
df = client.bars(symbol='600036', frequency=9, adjust='hfq')
```

### 3. 股票列表

```python
from mootdx import consts

# 获取上海股票列表
df_sh = client.stocks(market=consts.MARKET_SH)  # 或 market=1

# 获取深圳股票列表
df_sz = client.stocks(market=consts.MARKET_SZ)  # 或 market=0

# 返回字段：
# - code: 股票代码
# - name: 股票名称
# - market: 市场代码
```

### 4. 历史分时数据

```python
# 获取指定日期的分时数据
df = client.minutes(symbol='000001', date='20231215')

# 返回当天的分时行情（每分钟）
```

### 5. 分笔成交

```python
# 获取最新分笔成交
df = client.transaction(symbol='600036', start=0, offset=100)

# 获取历史分笔成交
df = client.transactions(symbol='000001', start=0, offset=100, date='20231215')
```

### 6. 财务信息（简略）

```python
# 获取最新财务信息（单条）
df = client.finance(symbol="600300")

# 返回字段（中文拼音）：
# - liutongguben: 流通股本
# - zongguben: 总股本
# - zongzichan: 总资产
# - zhuyingshouru: 主营收入
# - jinglirun: 净利润
# - meigujingzichan: 每股净资产
# 等 37 个字段
```

**注意**: `finance()` 只返回**最新一条**财务数据，不支持历史查询。要获取完整历史财务数据，必须使用 `Affair` 模块。

### 7. 除权除息

```python
# 获取除权除息信息
df = client.xdxr(symbol='600036')

# 返回字段：
# - date: 除权日期
# - category: 类型（送股/配股/分红）
# - fenhong: 分红金额
# - peigujia: 配股价
# 等
```

### 8. OHLC K线（带日期范围）

```python
# 按日期范围获取K线
df = client.k(symbol="600300", begin="2023-01-01", end="2023-12-31")

# 前复权
df = client.k(symbol="600300", begin="2023-01-01", end="2023-12-31", adjust='qfq')

# ohlc 是 k 的别名
df = client.ohlc(symbol="600300", begin="2023-01-01", end="2023-12-31")
```

---

## 本地数据读取 (Reader)

### 初始化

```python
from mootdx.reader import Reader

# 指定通达信安装目录
reader = Reader.factory(market='std', tdxdir='/mnt/c/new_tdx')
```

### 1. 日线数据

```python
# 读取本地日线数据
df = reader.daily(symbol='000001')

# 返回完整历史日线数据（从本地vipdoc目录读取）
```

### 2. 分钟数据

```python
# 读取本地分钟数据
df = reader.minute(symbol='000001')

# 返回本地存储的分钟线数据
```

### 3. 板块数据

```python
# 读取板块信息
df = reader.block()

# 返回所有板块及成分股
```

---

## 扩展功能 (Extras)

（根据需要补充）

---

## 字段对照表

### FINVALUE 财务数据字段（322个）

#### 基础字段
- `0` - 报告期 (YYMMDD格式，如 230630 = 2023年中报)

#### 每股指标 (1-7)
- `1` - 基本每股收益 (EPS)
- `2` - 扣非每股收益
- `3` - 每股未分配利润
- `4` - 每股净资产 (BPS)
- `5` - 每股资本公积
- `6` - 净资产收益率 (ROE)
- `7` - 每股经营现金流

#### 资产负债表 (8-73)
- `8` - 货币资金
- `11` - 应收账款
- `17` - 存货
- `21` - 流动资产合计
- `27` - 固定资产
- `40` - **资产总计**
- `41` - 短期借款
- `54` - 流动负债合计
- `63` - **负债合计**
- `64` - 实收资本（股本）
- `65` - 资本公积
- `68` - 未分配利润
- `72` - **所有者权益合计**

#### 利润表 (74-138)
- `74` - **营业收入**
- `75` - **营业成本**
- `77` - 销售费用
- `78` - 管理费用
- `80` - 财务费用
- `83` - 投资收益
- `86` - **营业利润**
- `90` - **利润总额**
- `92` - 所得税
- `93` - **净利润**
- `95` - **归母净利润**

#### 现金流量表 (139-322)
- `139` - 销售商品收到的现金
- `157` - **经营活动现金流入小计**
- `172` - **经营活动现金流出小计**
- `173` - **经营活动现金流量净额**
- `197` - **投资活动现金流量净额**
- `213` - **筹资活动现金流量净额**
- `222` - **现金及现金等价物净增加额**

**说明**:
1. 所有金额单位为**元**，股本单位为**股**
2. 空值显示为 0
3. 完整的 322 个字段详见原始文档 `fields.md`

---

## 关键使用场景

### 场景1: 获取股票最新财务数据

```python
from mootdx.affair import Affair

# 1. 获取文件列表
files = Affair.files()
latest_file = files[0]['filename']  # 最新的报告期

# 2. 下载数据
Affair.fetch(downdir='data', filename=latest_file)

# 3. 解析数据
df = Affair.parse(downdir='data', filename=latest_file)

# 4. 筛选特定股票
stock_data = df[df['code'] == '000001']
```

### 场景2: 获取日线数据

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

# 方法1: 使用 bars (推荐)
df = client.bars(symbol='000001', frequency=9, start=0, offset=800)

# 方法2: 使用 k (带日期范围)
df = client.k(symbol='000001', begin='2023-01-01', end='2023-12-31')

# 方法3: 使用 Reader (离线)
from mootdx.reader import Reader
reader = Reader.factory(market='std', tdxdir='/mnt/c/new_tdx')
df = reader.daily(symbol='000001')
```

### 场景3: 获取实时行情

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

# 批量获取
df = client.quotes(symbols=['000001', '600036', '600519'])

# 获取所有股票列表后批量查询
all_stocks = client.stocks(market=0)  # 深圳
prices = client.quotes(symbols=all_stocks['code'].tolist()[:100])
```

---

## 注意事项

1. **财务数据更新频率**:
   - 年报：每年4月30日前
   - 中报：每年8月31日前
   - 季报：对应季度结束后1个月内

2. **数据完整性**:
   - `Quotes.finance()` 只返回最新一条数据
   - 历史财务数据必须使用 `Affair` 模块下载 ZIP 文件

3. **性能优化**:
   - Reader 模式速度最快（本地读取）
   - Quotes 在线模式有速率限制
   - 建议使用 Reader + Affair 组合

4. **市场代码**:
   - `0` / `MARKET_SZ` - 深圳
   - `1` / `MARKET_SH` - 上海

5. **复权类型**:
   - `qfq` - 前复权（默认推荐）
   - `hfq` - 后复权
   - 不指定 - 不复权

---

**文档版本**: v1.0
**维护者**: SimTradeData Team
**最后更新**: 2025-09-30
