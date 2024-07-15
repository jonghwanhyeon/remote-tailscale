ARG registry
ARG image
FROM $registry/$image

ARG container_name
ARG uid
ARG gid
ARG user
ARG name
ARG email

# Install required packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        curl \
        locales \
        sudo \
        zsh \
    && rm -rf /var/lib/apt/lists/*

# Install tailscale
RUN curl --silent --show-error --location https://tailscale.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Install antigen
RUN mkdir -p /usr/local/share/antigen \
    && curl --silent --show-error --location git.io/antigen > /usr/local/share/antigen/antigen.zsh

# Since Tailscale SSH does not have default LANG variable,
# VSCode set LANG as en_US.UTF-8
RUN locale-gen en_US.UTF-8 && update-locale

# Add user without password and grant sudo privileges
RUN groupadd --gid=$gid "$user" \
    && useradd \
        --uid=$uid \
        --gid=$gid \
        --comment="remote-tailscale" \
        --create-home \
        --shell=/bin/zsh \
        "$user" \
    && passwd --delete "$user" \
    && echo "$user ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$user \
    && chmod u=r,g=r,o= /etc/sudoers.d/$user

# Create /workspace and make a sybolic link to /workspace
VOLUME /workspace
RUN runuser --user="$user" -- ln --symbolic /workspace /home/$user/workspace

# Configure zsh
COPY --chown=$uid:$gid scripts/.zshrc /home/$user/.zshrc
COPY --chown=$uid:$gid scripts/.spaceshiprc.zsh /home/$user/.spaceshiprc.zsh

# Configure Git
RUN runuser --user="$user" -- git config --global user.name "$name" \
    && test ! -z $email && runuser --user="$user" -- git config --global user.email "$email" || true

# Export container name for hostname of tailscale
ENV CONTAINER_NAME="$container_name"

COPY docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
