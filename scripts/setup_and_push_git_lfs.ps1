Param(
    [string]$remote = ""
)

Write-Host "Running Git LFS setup and push helper..."

git lfs install

Write-Host "Ensuring .gitattributes is added"
git add .gitattributes

Write-Host "Staging all changes"
git add -A

$status = git status --porcelain
if ($status) {
    git commit -m "Prepare repo and track large files with Git LFS" 
} else {
    Write-Host "No changes to commit"
}

if ($remote) {
    $existing = git remote
    if (-not ($existing -contains 'origin')) {
        git remote add origin $remote
        Write-Host "Added remote origin: $remote"
    } else {
        Write-Host "Remote 'origin' already exists"
    }
}

$branch = git rev-parse --abbrev-ref HEAD
if (-not $branch) { $branch = 'main' }

Write-Host "Pushing to origin/$branch (you may be prompted for credentials)"
git push -u origin $branch

Write-Host "Done. If push failed, verify the remote URL and your credentials."
