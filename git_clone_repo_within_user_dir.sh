GITUSER=$(echo $1 | cut -d / -f 4)
# GITREPO=$(echo $1 | cut -d / -f 2)

mkdir $GITUSER || echo 
cd $GITUSER || echo cd error
export GIT_TERMINAL_PROMPT=0
git clone $1 || echo git clone error
