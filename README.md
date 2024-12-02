# INE5420 - Computação Gráfica - 2024/2

## Sistema Gráfico Interativo

### Introdução

Consiste numa interface gráfica em que o usuário pode carregar arquivos.obj e/ou criar seus próprios elementos (pontos, linhas, polígonos) e manipulá-los de várias formas.

Essa documentação trará uma breve explicação de alguns dos principais elementos que orientaram a implementação desse sistema, assim como as ferramentas utilizadas. Por fim, uma explicação de como testar a aplicação e uma seção de dificuldades enfrentadas.

### Desenvolvimento

Esse SGI foi feito utilizando principalmente a biblioteca [PyQt5](https://pypi.org/project/PyQt5/), que fornece uma interface para o [Qt5](https://www.qt.io/), que por sua vez é uma biblioteca para criação de interfaces gráficas de usuário. 

O PyQt5 funciona por meio de Orientação Objetos utilizando sinais e slots, ou seja, implementando botões na GUI, por exemplo, gera um sinal que pode ser direcionado para uma função, que realiza um cálculo ou imprime um objeto na tela.

Para fazer a interface gráfica mais facilmente, há uma ferramenta chamada [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html), a qual pode ser observada na figura a seguir. Essa ferramenta permite criar layouts de GUI de forma gráfica e importar o .ui para o sistema. Dessa forma foi possível integrá-los ao código em python sem precisar implementar cada pequeno detalhe da interface gráfica, apenas manipulando os sinais com suas respectivas funções.

![Imagem da GUI do Qt Designer](image.png)

Na pasta "qt_design" tem todos os arquivos .ui que foram criados utilizando o Qt Designer, cada um deles representa uma interface do SGI.

O SGI foi implementado em etapas, seguindo as entregas da disciplina. Dessa forma, as seguintes funções foram implementadas:

1. Adicionar pontos, linhas e polígonos, assim como a capacidade de dar zoom e navegar pela window;
2. Transformações 2D, como rotações, translações e escalonamentos;
3. Clipping dos objetos, Cohen-Sutherland e Liang-Barsky;
4. Curvas 2D;
4. Objetos 3D e projeções da window;
5. Superfícies Bicúbicas;
6. Manipulação de arquivos .obj.

#### 1. Adicionando objetos e funções básicas de navegação

Para a adição de objetos 2D básicos, foi modelado dataclasses, as quais contém informações sobre os objetos, como nome, suas componenetes, cor, tipo, etc. 

![Dataclass representando um ponto](image-1.png)

Para a adição desses objetos, botões correspondentes aparecem na SGI, os quais tem campos de entrada para as coordenadas dos pontos/componentes e cor do objeto.

![Interface de adição de um ponto](image-2.png)

As funções de navegação "Zoom In", "Zoom Out" e mover a tela para alguma das quatro direções (esquerda, direita, baixo e cima) funcionam manipulando as coordenadas da window, X e Y máximos e mínimos. No caso das navegações, a fórmula de rotação é utilizada utilizando um vetor base que indica para qual direção a tela irá se mover. 

![Fórmula de rotação por um ângulo](image-3.png)

#### 2. Transformações 2D

As funções de transformação de objetos e da window foram implementadas considerando o conceito de coordenadas homogêneas, utilizando as multiplicações de matrizes para realizar essas operações. 

De acordo com o tipo de objeto, suas coordenadas são mapeadas para uma matriz e as transformações são aplicadas. Cada uma pede coordenadas de base para orientar a transformação. No caso da rotação da window, é recebido as coordenadas da rotação e em seguida manipulado o ângulo da window, variável que orienta o ângulo de todos os objetos da window e permite que todos os objetos dentro da window sofram a rotação esperada.

![Rotação de um objeto](image-4.png)

### 3. Clipping dos objetos

Clipping consiste na capacidade de recortar objetos da da window, para garantir que apenas os objetos relevantes sejam desenhados. Para realizar o clipping, uma "moldura" em vermelho foi adicionada à window, a qual permite ver quais objetos estão "dentro" e quais objetos não estão sendo desenhados por estarem "fora". 

![Exemplo de clipping em que parte da linha não está visível](image-5.png)

Isso é feito determinando-se quais coordenadas estão dentro da window e quais não estão. Isso é atualizado toda vez que uma transformação acontece. Além disso, dois algoritmos foram utilizados para realizar o clipping de linhas: Clipping de Cohen-Sutherland e Clipping de Liang-Barsky. Pelo primeiro foi criado uma versão simplificada de regiões para determinar os pontos dentro. Já o segundo faz uma melhoria do primeiro pelo cálculo das intersecções das linhas com as bordas da window. 

### 4. Curvas 2D

As curvas 2D implementadas nesse sistema são as curvas paramétricas de Bezier e as B-Splines. A primeira é definida com um conjunto de pontos de controle que determinarão o formato da curva, em que continuidade da mesma representa a "suavidade" da curva ou à ausência de descontinuidades da mesma. Já uma B-spline é uma curva ou superfície que é composta por segmentos de curvas polinomiais que se unem de forma suave. 

Elas foram implementadas de forma a receber do usuário a lista de pontos das curvas e a precisão, que representa a densidade da curva. Um valor menor de precisão resulta em uma curva mais detalhada (mais pontos gerados) e mais iterações são feitas pelo algoritmo. 

A curva de Bezier foi implementada considerando a interpolação e o número de pontos a ser utilizado como controle serão usados para gerar os outros. Através do método de blending, que gera os coeficientes de interpolação, a interpolação é feita e os produtos escalares dos pontos de controle são utilizados para gerar os novos pontos. 

Para a B-Spline, para cada ponto de controle é criado um subgrupo de pontos, a borda superior e os deltas (variação) dos pontos são calculados. As coordenadas são ajustadas com base nos cálculos dos deltas, os quais são progressivamente incrementados. 

### 5. 

