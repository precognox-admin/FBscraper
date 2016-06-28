library(testthat)
library(RSQLite)

RSQLite::SQLite()
drv <- SQLite()

setwd("../data/")
databases <- list.files()
activities <- c("Posts", "Comments", "Post_likes")
tables <- c("Posts", "Comments", "Post_likes", "People")

for (database in databases) {
  # connect to sqlite database
  db <- dbConnect(
    drv, dbname = database,
    loadable.extensions = TRUE, cache_size = NULL, synchronous = "off",
    flags = SQLITE_RWC, vfs = NULL
  )
  
  for (table in tables) {
    assign(paste0(table, "_author_id"),
           c(t(dbGetQuery(
             db, paste0("SELECT author_hash_id FROM ", table)
           ))))
  }
  
  for (activity in activities) {
    a <- get(paste0(activity, "_author_id"))
    print(paste("Testing:", database, activity))
    expect_that(length(which(a %in% People_author_id)), equals(length(a)))
    print("Ok")
  }
}