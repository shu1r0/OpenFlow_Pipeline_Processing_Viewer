# OpenFlow Pipeline Processing Viewer (OFP2V)
SDNを実現する技術にOpenFlowがある．OpenFlowコントローラ開発におけるネットワークの動作検証では，複数のツールを使いこなす必要があるため，開発者の負荷が大きい．そこで本研究では，OpenFlowコントローラ開発時におけるデバックの負担軽減を目的に，パケットの追跡を自動化しOpenFlowパイプライン処理を可視化するコントローラ開発支援システムを開発した．本システムは，仮想ネットワークでのパケットやスイッチの動作を分析し可視化する．これによりネットワークの把握が容易となり，デバック時における時間的コストや各ツールの学習コストの削減が期待できる


## ディレクトリ構成
```
$ tree -F -L 1 --dirsfirst
.
├── docs/  # document
├── src/   # server source
├── view/  # web client
├── web_server/  # web server
├── windows/  # environment for windows
├── Makefile
├── README.md
└── Vagrantfile

```

## Webクライアント


### Mininet Console

仮想ネットワークの設定を変更・可視化するためのユーザインターフェースです．
Webクライアント上で，ホストでシェルコマンドを実行したり，IPアドレスの変更を行うことができます．

![console](./docs/images/console.gif)

### 仮想ネットワークの作成
仮想ネットワークは，直感的な操作で作成できます．

![create_vnet](./docs/images/create_vnet.gif)

### OpenFlowパイプラインの可視化
OpenFlowスイッチのパイプラインを可視化する部分です．

![pipeline1](./docs/images/pipeline2.gif)

