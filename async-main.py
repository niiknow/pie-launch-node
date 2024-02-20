app.post("/github_webhook", include_in_schema=False)


async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    if payload.get("ref", None) != "refs/heads/main":
        raise HTTPException(200, "Not main branch.")

    def pull():
        try:
            subprocess.run(
                "git pull origin main",
                cwd=ROOT_PATH,
                shell=True,
                capture_output=True,
                check=True,
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.returncode, ROOT_PATH, e.stderr) from e

        return compile_all(game_id=None, force=True)

    background_tasks.add_task(pull)
    return {"status": "success"}
