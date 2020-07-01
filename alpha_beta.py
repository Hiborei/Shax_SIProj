import main

def minmax(node,depth,alpha,beta,maximizingPlayer):

# jeśli dochodzi do liscia
    if (depth == 0):
        return node.score

    if (maximizingPlayer):
        maxEval =  -10000
        for child in node.children:
            eval = minmax(child,depth-1,alpha,beta,False)
            maxEval =  max(maxEval,eval)
            alpha = max(alpha,maxEval)
            if (beta <= alpha):
                break
        return maxEval

    else:
        maxEval = 10000
        for child in node.children:
            eval = minmax(child,depth-1,alpha,beta,True)
            maxEval =  min(maxEval,eval)
            alpha = min(alpha,maxEval)
            if (beta <= alpha):
                break
        return maxEval


def minmax2(node,depth,alpha,beta,maximizingPlayer):

# jeśli dochodzi do liscia
    if (depth == 0):
        return node

    if (maximizingPlayer):
        maxEval = main.TreeBranch(None)
        maxEval.score = -10000
        for child in node.children:
            eval = minmax2(child,depth-1,alpha,beta,False)
            if(eval.score > maxEval.score):
                maxEval = eval

            alpha = max(alpha,maxEval.score)
            if (beta <= alpha):
                break
        return maxEval

    else:
        maxEval = main.TreeBranch(None)
        maxEval.score = 10000
        for child in node.children:
            eval = minmax2(child,depth-1,alpha,beta,True)
            if(eval.score < maxEval.score):
                maxEval = eval
            alpha = min(alpha,maxEval.score)
            if (beta <= alpha):
                break
        return maxEval
