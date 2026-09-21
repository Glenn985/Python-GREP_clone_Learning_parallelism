#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>
#include <ctype.h>

int hasRestriction(char *restrictions[], int restrictionCount, char *target) {
    for (int i = 0; i < restrictionCount; i++) {
        if (strcmp(restrictions[i], target) == 0) {
            return 1;
        }
    }
    return 0;
}


// Similar to your Python Search()
void Search(char *file_path, char *restrictions[], int restrictionCount, char *text) {

    clock_t start = clock();

    FILE *file = fopen(file_path, "r");

    if (file == NULL) {
        printf("Could not open file: %s\n", file_path);
        return;
    }

    char line[4096];
    int count = 0;

    int caseInsensitive =
        hasRestriction(restrictions, restrictionCount, "~a");

    while (fgets(line, sizeof(line), file)) {

        char *position = line;

        while (*position != '\0') {

            if (caseInsensitive) {

                int match = 1;

                for (int i = 0; text[i] != '\0'; i++) {

                    if (position[i] == '\0' ||
                        tolower((unsigned char)position[i]) !=
                        tolower((unsigned char)text[i])) {

                        match = 0;
                        break;
                    }
                }

                if (match) {
                    count++;
                    position += strlen(text);
                }
                else {
                    position++;
                }

            }

            else {

                char *found = strstr(position, text);

                if (found != NULL) {
                    count++;
                    position = found + strlen(text);
                }
                else {
                    break;
                }
            }
        }
    }

    fclose(file);

    double timeTaken =
        ((double)(clock() - start)) / CLOCKS_PER_SEC;

    printf("NO of recurrences: %d\n", count);
    printf("Time taken: %f\n", timeTaken);
}


// Similar to RecursiveSearch()
void RecursiveSearch(
    char *path,
    char *restrictions[],
    int restrictionCount,
    char *text
) {

    DIR *directory = opendir(path);

    if (directory == NULL) {
        printf("Path does not exist or cannot be opened: %s\n", path);
        return;
    }

    struct dirent *entry;

    while ((entry = readdir(directory)) != NULL) {

        // Ignore . and ..
        if (
            strcmp(entry->d_name, ".") == 0 ||
            strcmp(entry->d_name, "..") == 0
        ) {
            continue;
        }

        char fullPath[4096];

        snprintf(
            fullPath,
            sizeof(fullPath),
            "%s/%s",
            path,
            entry->d_name
        );

        struct stat info;

        if (stat(fullPath, &info) != 0) {
            continue;
        }

        // If directory → recursively search it
        if (S_ISDIR(info.st_mode)) {

            RecursiveSearch(
                fullPath,
                restrictions,
                restrictionCount,
                text
            );
        }

        // If normal file
        else if (S_ISREG(info.st_mode)) {

            char *extension = strrchr(entry->d_name, '.');

            // equivalent to checking for .txt
            if (
                extension != NULL &&
                strcmp(extension, ".txt") == 0
            ) {

                printf("Searching: %s\n", fullPath);

                Search(
                    fullPath,
                    restrictions,
                    restrictionCount,
                    text
                );
            }
        }
    }

    closedir(directory);
}


int main(int argc, char *argv[]) {

    if (argc < 3) {
        printf("There are not enough parameters\n");
        return 1;
    }

    printf("PID: %d\n", getpid());

    char *command = argv[1];

    if (strcmp(command, "PGREP") == 0) {

        char *restrictions[100];
        int restrictionCount = 0;

        // Find ~r, ~a, etc.
        for (int i = 2; i < argc - 1; i++) {

            if (
                argv[i][0] == '~' &&
                strlen(argv[i]) == 2
            ) {

                restrictions[restrictionCount] = argv[i];
                restrictionCount++;
            }
        }

        printf("Restrictions: ");

        for (int i = 0; i < restrictionCount; i++) {
            printf("%s ", restrictions[i]);
        }

        printf("\n");

        // Last argument = search text
        char *text = argv[argc - 1];


        // ~r means recursive
        if (
            hasRestriction(
                restrictions,
                restrictionCount,
                "~r"
            )
        ) {

            char *path = ".";

            // Find directory argument
            for (int i = 2; i < argc - 1; i++) {

                struct stat info;

                if (
                    argv[i][0] != '~' &&
                    stat(argv[i], &info) == 0 &&
                    S_ISDIR(info.st_mode)
                ) {

                    path = argv[i];
                    break;
                }
            }

            RecursiveSearch(
                path,
                restrictions,
                restrictionCount,
                text
            );
        }

        else {

            char *fileName = NULL;

            // Find file argument
            for (int i = 2; i < argc - 1; i++) {

                if (
                    argv[i][0] != '~' &&
                    strchr(argv[i], '.') != NULL
                ) {

                    fileName = argv[i];
                    break;
                }
            }

            if (fileName == NULL) {
                printf("No file name was provided\n");
                return 1;
            }

            Search(
                fileName,
                restrictions,
                restrictionCount,
                text
            );
        }
    }

    return 0;
}