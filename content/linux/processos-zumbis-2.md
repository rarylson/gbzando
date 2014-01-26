Title: Processos zumbis: Tratando corretamente (parte 2)
Date: 2013-11-8 18:10
Tags: linux, shell, c, real
Slug: processos-zumbis-2
Category: Linux
Author: Rarylson Freitas
Summary: Saiba como evitar que seu software gere processos zumbis. Neste artigo, iremos desenvolver corretamente programas em C que não geram processos zumbis. Iremos também analisar como alguns softwares do mundo real tratam este tipo de processo. Por fim, iremos apresentar um exemplo real de software onde uma falha permitia criar infindandamente processos zumbis no sistema.
Status: draft

No primeiro artigo [Processos zumbis: Introdução (parte 1)]({filename}processos-zumbis.md), mostramos o que são processos zumbis e quais são os problemas que podem causar.

Neste artigo, iremos mostrar como evitá-los: mostraremos como desenvolver uma aplicação que execute continuamente sem gerar um alto número de processos zumbis.

Iremos também apresentar situações em que processos zumbis não precisam ser tratados ou em que basta tratá-los de tempo em tempo.

Por fim, iremos mostrar um exemplo real onde o software **Symantec Backup Exec**, em uma versão mais antiga, não tratava corretamente o fim de seus processos filhos, gerando vários processos zumbis no sistema. Iremos mostrar também o _workarround_ utilizado para contornar a situação.

Recaptulando
------------

Dentre os conceitos mais importantes do [artigo passado]({filename}processos-zumbis.md), podemos citar:

- [Processo zumbis](http://en.wikipedia.org/wiki/Zombie_process), também chamados de _zombies_ ou _defuncts_, são processos que terminaram a execução, tiveram seus recursos desalocados, mas ainda possuem uma entrada na tabela de processos;
- Em grande número, podem esgotar o número de PIDs do sistema;
- Processos, ao finalizar sua execução, permanecem na tabela de processos para que seu processo pai possa ser notificado do fim de sua execução, analisar o código que o filho retornou, e executar ações necessárias para manter o correto funcionamento da aplicação;
  - Assim, _deamons_ deveriam tratar corretamente seus processos filhos, retirando adequadamente suas entradas da tabela de processos a medida que estes vão morrendo.

Tratando corretamente
---------------------



Referências
-----------

- [Signals (and Zombie and SIGCHLD)](http://www.win.tue.nl/~aeb/linux/lk/lk-5.html)
- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
